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

Web UI — start the local server and open the printed address:

```bash
python app.py            # -> http://127.0.0.1:8000   (PORT=... to change)
```

Pick a model, write a prompt, and it submits the job, polls it, and shows the
result inline. If no key is set the page shows a field for one; a key entered
there is held in memory by the local server for as long as it runs, and is
never written to disk.

Command line:

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

Both paths submit the job, poll until it reaches a terminal state, and give you
the resulting asset URL. Endpoint details and raw `curl` equivalents are in
[`RUNBOOK.md`](RUNBOOK.md).

By default the server binds to `127.0.0.1`, so nothing outside your machine can
reach it. Your key and prompts go to `platform.higgsfield.ai` and nowhere else.

## Video options

Video models can carry extra settings. They appear under the model picker only
for models that declare them, and every one starts at `default`:

| model | settings | prompt limit |
| --- | --- | --- |
| `minimax-h3` | aspect ratio, duration (4–15s) | 2000 characters |
| `kling-3.0` | aspect ratio, duration (3–15s) | — |
| `veo-3.1-fast` | aspect ratio, duration (4/6/8s), quality | — |
| `ltx-2.5-pro` | — | — |

A setting left at `default` is **not sent**, so a request you did not touch is
the same `{"prompt": ...}` it has always been. Values outside the allowed range
are dropped rather than forwarded, and image models are untouched.

All of it lives in `VIDEO_OPTIONS` at the top of `generate.py` — one table, one
place to change a range, add a model, or set a prompt limit.

## Hosting it (so you can use it from a phone)

The UI needs a host that allows outbound HTTPS. A published claude.ai artifact
cannot do this job — its sandbox blocks requests to every external host, so a
page there can never reach `platform.higgsfield.ai` whatever key it holds.

One tap, no configuration:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/the0genius/test)

Sign in with GitHub, accept the defaults, and Render hands back an
`https://….onrender.com` URL. Open it, type your key id and secret into the
page, and generate. The key lives in the server's memory until the instance
restarts, and never touches the browser after you submit it.

### Optional hardening

| variable | why |
| --- | --- |
| `APP_PASSWORD` | puts a sign-in step in front of the UI |
| `HF_API_KEY_ID` / `HF_API_KEY_SECRET` | preload the key so nobody has to type it |

Preloading the key on a public URL without `APP_PASSWORD` would let anyone who
finds the URL spend your credit, so the app refuses to start in that one
combination. Everything else runs.
