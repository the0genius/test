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
}

TERMINAL = {"completed", "failed", "nsfw", "canceled"}


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

    response = requests.post(
        "https://platform.higgsfield.ai" + MODELS[model],
        headers=headers,
        json={"prompt": prompt},
        timeout=60,
    )
    response.raise_for_status()
    job = response.json()
    print("request:", job["request_id"])

    delay = 2
    while True:
        time.sleep(delay + random.random() / 2)
        response = requests.get(job["status_url"], headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        print("status:", result["status"])

        if result["status"] in TERMINAL:
            break

        delay = min(delay * 1.5, 10)

    if result["status"] != "completed":
        print(result.get("error", result["status"]))
        return 1

    if "images" in result:
        print(result["images"][0]["url"])
    else:
        print(result["video"]["url"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
