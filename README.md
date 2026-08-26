# media-inference-worker

Small command-line client for Higgsfield text-to-image and text-to-video
inference endpoints. Vendored from
[framepipe-dev/media-inference-worker](https://github.com/framepipe-dev/media-inference-worker).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then add your own key
```

`generate.py` reads `HF_API_KEY_ID` and `HF_API_KEY_SECRET` from the
environment, falling back to a local `.env`. Get a key from
[platform.higgsfield.ai](https://platform.higgsfield.ai). `.env` is gitignored —
keep credentials out of commits.

## Usage

```bash
python generate.py qwen-image-3 "Editorial portrait, hard flash, 35mm grain"
```

Available models:

| name | kind |
| --- | --- |
| `qwen-image-3` | image |
| `nano-banana-2-lite` | image |
| `gpt-image-2` | image |
| `minimax-h3` | video |
| `ltx-2.5-pro` | video |
| `kling-3.0` | video |
| `veo-3.1-fast` | video |

The script submits the job, polls until it reaches a terminal state, and prints
the resulting asset URL. Endpoint details and raw `curl` equivalents are in
[`RUNBOOK.md`](RUNBOOK.md).

## Note on the upstream repository

Upstream ships a committed `.env` holding live service-account credentials that
its README describes as copied from elsewhere, with the author noting they did
not know when the key would be rotated. Those credentials were deliberately not
carried over here — this copy authenticates only with a key you supply.
