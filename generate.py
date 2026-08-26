#!/usr/bin/env python3

import os
import random
import sys
import time
from pathlib import Path

import requests


MODELS = {
    "qwen-image-3": "/alibaba/qwen-image-3/text-to-image",
    "nano-banana-2-lite": "/nano-banana-2/lite/text-to-image",
    "gpt-image-2": "/openai/gpt-image-2",
    "minimax-h3": "/minimax/h3/text-to-video",
    "ltx-2.5-pro": "/lightricks/ltx-2.5/text-to-video/pro",
    "kling-3.0": "/kling-video/v3.0/std/text-to-video",
    "veo-3.1-fast": "/veo3.1/fast/text-to-video",
    # Path not in RUNBOOK.md — inferred from the pattern of the others.
    # If this 404s, correct the path here and nothing else needs touching.
    "seedance-2.5": "/bytedance/seedance-2.5/text-to-video",
}

TERMINAL = {"completed", "failed", "nsfw", "canceled"}

BASE = "https://platform.higgsfield.ai"

# Optional extras for the video models, taken from the model catalogue. Every
# control defaults to unset and an unset control is never sent, so a request
# nobody touched is the same {"prompt": ...} it has always been.
# ltx-2.5-pro is absent on purpose: no published parameters to go on.
VIDEO_OPTIONS = {
    "minimax-h3": {
        "prompt_max": 2000,
        "controls": [
            {"name": "aspect_ratio", "label": "Aspect ratio", "kind": "choice",
             "options": ["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]},
            {"name": "duration", "label": "Duration", "kind": "number",
             "min": 4, "max": 15, "unit": "s"},
            # The catalogue lists one tier for this model; kept so the control
            # is explicit rather than missing.
            {"name": "resolution", "label": "Quality", "kind": "choice",
             "options": ["2K"]},
        ],
    },
    "seedance-2.5": {
        "controls": [
            {"name": "aspect_ratio", "label": "Aspect ratio", "kind": "choice",
             "options": ["auto", "21:9", "16:9", "4:3", "1:1", "3:4", "9:16"]},
            {"name": "duration", "label": "Duration", "kind": "number",
             "min": 4, "max": 30, "unit": "s"},
            {"name": "resolution", "label": "Quality", "kind": "choice",
             "options": ["480p", "720p", "1080p"]},
            {"name": "generate_audio", "label": "Audio", "kind": "bool"},
            {"name": "bitrate_mode", "label": "Bitrate", "kind": "choice",
             "options": ["standard", "high"]},
        ],
    },
    "kling-3.0": {
        "controls": [
            {"name": "aspect_ratio", "label": "Aspect ratio", "kind": "choice",
             "options": ["16:9", "9:16", "1:1"]},
            {"name": "duration", "label": "Duration", "kind": "number",
             "min": 3, "max": 15, "unit": "s"},
        ],
    },
    "veo-3.1-fast": {
        "controls": [
            {"name": "aspect_ratio", "label": "Aspect ratio", "kind": "choice",
             "options": ["16:9", "9:16"]},
            {"name": "duration", "label": "Duration", "kind": "number",
             "options": [4, 6, 8], "unit": "s"},
            {"name": "quality", "label": "Quality", "kind": "choice",
             "options": ["basic", "high", "ultra"]},
        ],
    },
}


def option_specs(model):
    return VIDEO_OPTIONS.get(model, {}).get("controls", [])


def prompt_limit(model):
    return VIDEO_OPTIONS.get(model, {}).get("prompt_max")


def clean_options(model, given):
    """Keep only controls this model declares, with values it allows."""
    picked = {}
    if not isinstance(given, dict):
        return picked
    for spec in option_specs(model):
        raw = given.get(spec["name"])
        if raw is None or raw == "":
            continue
        if spec["kind"] == "number":
            try:
                value = int(raw)
            except (TypeError, ValueError):
                continue
            if spec.get("options") and value not in spec["options"]:
                continue
            if "min" in spec and value < spec["min"]:
                continue
            if "max" in spec and value > spec["max"]:
                continue
        elif spec["kind"] == "bool":
            if raw in (True, "true"):
                value = True
            elif raw in (False, "false"):
                value = False
            else:
                continue
        else:
            value = str(raw)
            if value not in spec["options"]:
                continue
        picked[spec["name"]] = value
    return picked


def build_headers(key_id, key_secret):
    return {
        "Authorization": f"Key {key_id}:{key_secret}",
        "Content-Type": "application/json",
    }


def submit(model, prompt, headers, options=None):
    payload = {"prompt": prompt}
    payload.update(options or {})
    response = requests.post(
        BASE + MODELS[model],
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def check(status_url, headers):
    response = requests.get(status_url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def asset_url(result):
    if "images" in result:
        return result["images"][0]["url"]
    return result["video"]["url"]


def load_env():
    env_file = Path(__file__).with_name(".env")
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            name, value = line.split("=", 1)
            os.environ.setdefault(name.strip(), value.strip())


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in MODELS:
        names = " | ".join(MODELS)
        print(f'usage: python generate.py [{names}] "prompt"')
        return 1

    load_env()
    model = sys.argv[1]
    prompt = " ".join(sys.argv[2:])
    try:
        auth = (
            f"Key {os.environ['HF_API_KEY_ID']}:"
            f"{os.environ['HF_API_KEY_SECRET']}"
        )
    except KeyError as missing:
        print(f"{missing.args[0]} is not set.")
        print("Copy .env.example to .env and add your own Higgsfield key,")
        print("or export both variables in your shell.")
        return 1
    headers = {"Authorization": auth, "Content-Type": "application/json"}

    job = submit(model, prompt, headers)
    print("request:", job["request_id"])

    delay = 2
    while True:
        time.sleep(delay + random.random() / 2)
        result = check(job["status_url"], headers)
        print("status:", result["status"])

        if result["status"] in TERMINAL:
            break

        delay = min(delay * 1.5, 10)

    if result["status"] != "completed":
        print(result.get("error", result["status"]))
        return 1

    print(asset_url(result))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
