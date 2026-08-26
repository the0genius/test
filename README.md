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

## Hosting it (so you can use it from a phone)

The UI needs a host that allows outbound HTTPS. A published claude.ai artifact
cannot do this job — its sandbox blocks requests to every external host, so a
page there can never reach `platform.higgsfield.ai` whatever key it holds.

There is a `Dockerfile`, and `render.yaml` for a one-click Render blueprint.
Anywhere that runs a container works the same way. Set three environment
variables:

| variable | why |
| --- | --- |
| `APP_PASSWORD` | **required** — gates the UI |
| `HF_API_KEY_ID` | your Higgsfield key id |
| `HF_API_KEY_SECRET` | your Higgsfield key secret |

With the key in the environment, it never appears in the page at all — the
browser only ever sends prompts.

**The password is not optional.** A reachable instance holding your API key is a
way for anyone with the URL to spend your credit, so the app refuses to start
when `HOST` is anything but loopback and `APP_PASSWORD` is unset. Sessions are
HttpOnly cookies, `Secure` behind an HTTPS edge, and wrong guesses are throttled
to ten per five minutes.

## Note on the upstream repository

Upstream ships a committed `.env` holding live service-account credentials that
its README describes as copied from elsewhere, with the author noting they did
not know when the key would be rotated. Those credentials were deliberately not
carried over here — this copy authenticates only with a key you supply.
