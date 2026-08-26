# inference notes

```text
base: https://platform.higgsfield.ai
auth: Authorization: Key <key_id>:<secret>
```

## models

```text
qwen-image-3  POST /alibaba/qwen-image-3/text-to-image
nano-banana-2-lite POST /nano-banana-2/lite/text-to-image
gpt-image-2   POST /openai/gpt-image-2
minimax-h3    POST /minimax/h3/text-to-video
ltx-2.5-pro   POST /lightricks/ltx-2.5/text-to-video/pro
kling-3.0     POST /kling-video/v3.0/std/text-to-video
veo-3.1-fast  POST /veo3.1/fast/text-to-video
```

All of them accept a `prompt`.

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
