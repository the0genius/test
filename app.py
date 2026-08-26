#!/usr/bin/env python3

import hmac
import json
import os
import secrets
import time
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

from generate import (
    BASE,
    MODELS,
    TERMINAL,
    asset_url,
    build_headers,
    accepts_reference,
    check,
    clean_options,
    load_env,
    option_specs,
    prompt_limit,
    reference_payload,
    submit,
    upload_bytes,
)


HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
PASSWORD = os.environ.get("APP_PASSWORD", "")

LOOPBACK = {"127.0.0.1", "::1", "localhost"}

MAX_UPLOAD = 20 * 1024 * 1024

# Held in memory for the life of the process, never written to disk.
KEY = {"id": "", "secret": ""}

SESSIONS = set()
ATTEMPTS = []


def kind(model):
    return "video" if "text-to-video" in MODELS[model] else "image"


def detail_of(payload, limit=400):
    """Whatever explanation the API put in a body or a job result."""
    if isinstance(payload, str):
        return payload.strip()[:limit]
    if not isinstance(payload, dict):
        return str(payload)[:limit] if payload else ""
    for key in ("detail", "message", "error", "reason", "failure_reason", "description"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:limit]
        if isinstance(value, (dict, list)) and value:
            return json.dumps(value)[:limit]
    return ""


def describe(err):
    response = getattr(err, "response", None)
    if response is None:
        return f"could not reach {BASE}"
    if response.status_code in (401, 403):
        return "the API rejected the key — check it is correct and still active"
    if response.status_code == 429:
        return "rate limited, or the account is out of credit"
    if response.status_code == 404:
        return "no endpoint at that path — the model's path in MODELS looks wrong"
    try:
        body = response.json()
    except ValueError:
        body = (response.text or "").strip()
    said = detail_of(body)
    if said:
        return f"the API returned {response.status_code}: {said}"
    return f"the API returned {response.status_code}"


def throttled():
    now = time.time()
    ATTEMPTS[:] = [t for t in ATTEMPTS if now - t < 300]
    return len(ATTEMPTS) >= 10


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, status, payload, cookie=None):
        self.send_bytes(status, json.dumps(payload).encode(), "application/json", cookie)

    def send_bytes(self, status, body, content_type, cookie=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > 64_000:
            return {}
        return json.loads(self.rfile.read(length) or b"{}")

    def secure(self):
        # Platforms terminate TLS at the edge and forward this header.
        return self.headers.get("X-Forwarded-Proto", "").split(",")[0].strip() == "https"

    def authed(self):
        if not PASSWORD:
            return True
        jar = SimpleCookie(self.headers.get("Cookie", ""))
        token = jar["sr_session"].value if "sr_session" in jar else ""
        return bool(token) and token in SESSIONS

    def do_GET(self):
        route = urlparse(self.path)
        if route.path == "/":
            page = Path(__file__).with_name("index.html").read_bytes()
            return self.send_bytes(200, page, "text/html; charset=utf-8")
        if route.path == "/api/config":
            return self.send_json(200, {
                "needs_password": bool(PASSWORD),
                "authed": self.authed(),
                "models": [{
                    "name": n,
                    "kind": kind(n),
                    "controls": option_specs(n),
                    "prompt_max": prompt_limit(n),
                    "reference": accepts_reference(n),
                } for n in MODELS],
                "key_configured": bool(KEY["id"] and KEY["secret"]),
                "key_from_env": bool(os.environ.get("HF_API_KEY_ID")),
            })
        if not self.authed():
            return self.send_json(401, {"error": "not signed in"})
        if route.path == "/api/status":
            return self.get_status(parse_qs(route.query).get("url", [""])[0])
        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        route = urlparse(self.path)
        if route.path == "/api/login":
            return self.login()
        if not self.authed():
            return self.send_json(401, {"error": "not signed in"})
        if route.path == "/api/key":
            return self.set_key()
        if route.path == "/api/upload":
            return self.take_upload()
        if route.path == "/api/generate":
            return self.start_job()
        self.send_json(404, {"error": "not found"})

    def login(self):
        if not PASSWORD:
            return self.send_json(400, {"error": "this instance has no password set"})
        if throttled():
            return self.send_json(429, {"error": "too many attempts — wait a few minutes"})
        given = (self.read_body().get("password") or "")
        if not hmac.compare_digest(given, PASSWORD):
            ATTEMPTS.append(time.time())
            return self.send_json(401, {"error": "wrong password"})
        token = secrets.token_urlsafe(32)
        SESSIONS.add(token)
        flags = "HttpOnly; SameSite=Strict; Path=/; Max-Age=43200"
        if self.secure():
            flags += "; Secure"
        self.send_json(200, {"authed": True}, cookie=f"sr_session={token}; {flags}")

    def set_key(self):
        data = self.read_body()
        key_id = (data.get("key_id") or "").strip()
        key_secret = (data.get("key_secret") or "").strip()
        if not key_id or not key_secret:
            return self.send_json(400, {"error": "both the key id and secret are required"})
        KEY["id"], KEY["secret"] = key_id, key_secret
        self.send_json(200, {"key_configured": True})

    def take_upload(self):
        content_type = (self.headers.get("Content-Type") or "").split(";")[0].strip()
        if not content_type.startswith(("image/", "video/", "audio/")):
            return self.send_json(400, {"error": "only an image, video or audio file"})
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return self.send_json(400, {"error": "that file came through empty"})
        if length > MAX_UPLOAD:
            return self.send_json(400, {
                "error": f"file is over the {MAX_UPLOAD // (1024 * 1024)} MB limit"
            })
        if not (KEY["id"] and KEY["secret"]):
            return self.send_json(400, {"error": "no API key set"})

        try:
            url = upload_bytes(self.rfile.read(length), content_type,
                               build_headers(KEY["id"], KEY["secret"]))
        except requests.RequestException as err:
            return self.send_json(502, {"error": describe(err)})
        except (KeyError, ValueError):
            return self.send_json(502, {"error": "the upload endpoint answered in an unexpected shape"})
        self.send_json(200, {"url": url})

    def start_job(self):
        data = self.read_body()
        model = data.get("model")
        prompt = (data.get("prompt") or "").strip()
        if model not in MODELS:
            return self.send_json(400, {"error": "unknown model"})
        if not prompt:
            return self.send_json(400, {"error": "a prompt is required"})
        if not (KEY["id"] and KEY["secret"]):
            return self.send_json(400, {"error": "no API key set"})

        limit = prompt_limit(model)
        if limit and len(prompt) > limit:
            return self.send_json(400, {
                "error": f"prompt is {len(prompt)} characters; {model} takes at most {limit}"
            })

        options = clean_options(model, data.get("options"))

        reference = (data.get("reference") or "").strip()
        if reference:
            if not accepts_reference(model):
                return self.send_json(400, {"error": f"{model} does not take a reference"})
            if not reference.startswith("https://"):
                return self.send_json(400, {"error": "a reference must be an https URL"})
            options.update(reference_payload(model, reference))

        try:
            job = submit(model, prompt, build_headers(KEY["id"], KEY["secret"]), options)
        except requests.RequestException as err:
            return self.send_json(502, {"error": describe(err)})

        self.send_json(200, {
            "request_id": job.get("request_id", ""),
            "status_url": job.get("status_url", ""),
            "status": job.get("status", "queued"),
        })

    def get_status(self, status_url):
        # The URL comes back through the browser, so only follow our own host.
        if not status_url.startswith(BASE + "/"):
            return self.send_json(400, {"error": "unexpected status url"})
        if not (KEY["id"] and KEY["secret"]):
            return self.send_json(400, {"error": "no API key set"})

        try:
            result = check(status_url, build_headers(KEY["id"], KEY["secret"]))
        except requests.RequestException as err:
            return self.send_json(502, {"error": describe(err)})

        status = result.get("status", "unknown")
        payload = {"status": status, "done": status in TERMINAL}
        if status == "completed":
            try:
                payload["url"] = asset_url(result)
            except (KeyError, IndexError):
                payload["error"] = "finished, but the response carried no asset"
        elif payload["done"]:
            said = detail_of(result)
            leftover = {k: v for k, v in result.items()
                        if k not in ("status", "id", "request_id", "images", "video")}
            if said:
                payload["error"] = f"{status}: {said}"
            elif leftover:
                payload["error"] = f"{status}: {json.dumps(leftover)[:400]}"
            else:
                payload["error"] = f"{status} (the API gave no reason)"
        self.send_json(200, payload)


def main():
    load_env()
    KEY["id"] = os.environ.get("HF_API_KEY_ID", "")
    KEY["secret"] = os.environ.get("HF_API_KEY_SECRET", "")

    # An open instance that already holds a key hands it to anyone with the
    # URL. An open instance with no key just shows an empty form, so allow it.
    public = HOST not in LOOPBACK
    if public and not PASSWORD and KEY["id"]:
        print("refusing to start: a public instance with a key baked in and no")
        print("APP_PASSWORD lets anyone with the URL spend your credit.")
        print("Either set APP_PASSWORD, or drop the key vars and type the key in the page.")
        return 1

    where = "http://127.0.0.1:%d" % PORT if HOST in LOOPBACK else "port %d" % PORT
    print(f"media-inference-worker UI  ->  {where}")
    if PASSWORD:
        print("password required")
    elif public:
        print("open to anyone with the URL — the key you type is live until restart")
    else:
        print("no password (loopback only)")
    if KEY["id"] and KEY["secret"]:
        print("key loaded from the environment")
    else:
        print("no key found — paste one into the page")

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
