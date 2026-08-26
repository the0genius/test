#!/usr/bin/env python3

import json
import os
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
    check,
    load_env,
    submit,
)


HOST = "127.0.0.1"
PORT = int(os.environ.get("PORT", "8000"))

# Held in memory for the life of the process, never written to disk.
KEY = {"id": "", "secret": ""}


def kind(model):
    return "video" if "text-to-video" in MODELS[model] else "image"


def describe(err):
    response = getattr(err, "response", None)
    if response is None:
        return f"could not reach {BASE}"
    if response.status_code in (401, 403):
        return "the API rejected the key — check it is correct and still active"
    if response.status_code == 429:
        return "rate limited, or the account is out of credit"
    return f"the API returned {response.status_code}"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, status, payload):
        self.send_bytes(status, json.dumps(payload).encode(), "application/json")

    def send_bytes(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        route = urlparse(self.path)
        if route.path == "/":
            page = Path(__file__).with_name("index.html").read_bytes()
            return self.send_bytes(200, page, "text/html; charset=utf-8")
        if route.path == "/api/config":
            return self.send_json(200, {
                "models": [{"name": n, "kind": kind(n)} for n in MODELS],
                "key_configured": bool(KEY["id"] and KEY["secret"]),
            })
        if route.path == "/api/status":
            return self.get_status(parse_qs(route.query).get("url", [""])[0])
        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        route = urlparse(self.path)
        if route.path == "/api/key":
            return self.set_key()
        if route.path == "/api/generate":
            return self.start_job()
        self.send_json(404, {"error": "not found"})

    def set_key(self):
        data = self.read_body()
        key_id = (data.get("key_id") or "").strip()
        key_secret = (data.get("key_secret") or "").strip()
        if not key_id or not key_secret:
            return self.send_json(400, {"error": "both the key id and secret are required"})
        KEY["id"], KEY["secret"] = key_id, key_secret
        self.send_json(200, {"key_configured": True})

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

        try:
            job = submit(model, prompt, build_headers(KEY["id"], KEY["secret"]))
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
            payload["error"] = result.get("error") or status
        self.send_json(200, payload)


def main():
    load_env()
    KEY["id"] = os.environ.get("HF_API_KEY_ID", "")
    KEY["secret"] = os.environ.get("HF_API_KEY_SECRET", "")

    print(f"media-inference-worker UI  ->  http://{HOST}:{PORT}")
    if KEY["id"] and KEY["secret"]:
        print("key loaded from the environment")
    else:
        print("no key found — paste one into the page (it stays on this machine)")

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
