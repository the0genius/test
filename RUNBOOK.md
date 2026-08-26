# inference notes

```text
base: https://platform.higgsfield.ai
auth: Authorization: Key <key_id>:<secret>     <- the model paths below
      hf-api-key: <key_id>                     <- the /files and /v1 paths
      hf-secret: <secret>
```

One host, one key, **two auth schemes**. The model endpoints below take the
`Authorization` header. The `/files/...` and `/v1/...` endpoints (the ones the
official SDK drives) take the `hf-api-key` / `hf-secret` pair instead, and
answer 401 to the other one.

`403` on these endpoints means **out of credits**, not a bad key — the SDK maps
it to its NotEnoughCreditsError.

## models

```text
qwen-image-3  POST /alibaba/qwen-image-3/text-to-image
nano-banana-2-lite POST /nano-banana-2/lite/text-to-image
gpt-image-2   POST /openai/gpt-image-2
minimax-h3    POST /minimax/h3/text-to-video
ltx-2.5-pro   POST /lightricks/ltx-2.5/text-to-video/pro
kling-3.0     POST /kling-video/v3.0/std/text-to-video
veo-3.1-fast  POST /veo3.1/fast/text-to-video
seedance-2.5  POST /bytedance/seedance-2.5/text-to-video   (unverified)
```

All of them accept a `prompt`.

`seedance-2.5` was not in these notes. Its path follows the provider-first shape
of `/minimax/h3/...` and `/lightricks/ltx-2.5/...`, but the other Bytedance and
Google models here are named after the model family rather than the provider
(`/nano-banana-2/lite/...`, `/veo3.1/fast/...`), so the alternatives worth trying
if it does not resolve are:

```text
/seedance-2.5/text-to-video
/seedance/v2.5/text-to-video
/bytedance/seedance-2-5/text-to-video
```

## qwen image

```bash
source .env

curl https://platform.higgsfield.ai/alibaba/qwen-image-3/text-to-image \
  -H "Authorization: Key ${HF_API_KEY_ID}:${HF_API_KEY_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Editorial portrait, hard flash, 35mm grain"}'
```

## minimax video

```bash
source .env

curl https://platform.higgsfield.ai/minimax/h3/text-to-video \
  -H "Authorization: Key ${HF_API_KEY_ID}:${HF_API_KEY_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"A silver coupe driving through rain at night"}'
```

## ltx video

```bash
source .env

curl https://platform.higgsfield.ai/lightricks/ltx-2.5/text-to-video/pro \
  -H "Authorization: Key ${HF_API_KEY_ID}:${HF_API_KEY_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Handheld shot following a runner through an empty station"}'
```

The first response is only a job:

```json
{
  "status": "queued",
  "request_id": "...",
  "status_url": "https://platform.higgsfield.ai/requests/.../status",
  "cancel_url": "https://platform.higgsfield.ai/requests/.../cancel"
}
```

GET `status_url` with the same authorization header until the status is
`completed`, `failed`, `nsfw`, or `canceled`.

Images are returned in `images[0].url`. Videos are returned in `video.url`.

## reference media

From the official SDK (`higgsfield-ai/higgsfield-js`), same host and same key,
but with the `hf-api-key` / `hf-secret` headers rather than `Authorization`:

```text
POST /files/generate-upload-url   {"content_type": "image/jpeg"}
  -> {"upload_url": "...", "public_url": "..."}
PUT  <upload_url>                 raw bytes, Content-Type only
```

The presigned `upload_url` carries its own auth — do not send the API key with
the bytes. `public_url` is then what a generation refers to.

The SDK's own endpoints wrap that URL as
`input_images: [{"type": "image_url", "image_url": "..."}]`, but those are its
`/v1/...` endpoints (`/v1/image2video/dop`, `/v1/text2image/soul`), not the
model paths above. How these model endpoints want a reference named is
**unverified** — `REFERENCE_SHAPES` in `generate.py` holds the candidates and
`REFERENCE_MODELS` picks one per model.
