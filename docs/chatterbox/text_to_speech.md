# Chatterbox Text-to-Speech API Endpoint Documentation

**Author:** NetzPrinz aka Oliver Hees
**Integration:** Chatterbox TTS by Resemble AI

## Overview

The `/v1/chatterbox/text-to-speech` endpoint provides advanced text-to-speech functionality using the Chatterbox TTS model. This endpoint supports multiple languages, emotion control, and ultra-low latency speech generation. The endpoint leverages the application's queuing system for asynchronous processing of potentially time-consuming TTS operations.

### Key Features
- **Multilingual Support**: 23 languages supported (when using multilingual model)
- **High Quality**: 0.5B parameter model trained on 0.5M hours of data
- **Emotion Control**: Adjustable emotion intensity
- **GPU Acceleration**: CUDA support for faster generation
- **Watermarked Audio**: All generated audio includes watermarking

## Endpoint

- **URL**: `/v1/chatterbox/text-to-speech`
- **Method**: `POST`

## Request

### Headers

- `x-api-key`: Required. Your API authentication key.

### Body Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | String | Yes | - | Text to convert to speech (1-5000 characters) |
| `language` | String | No | "en" | Language code (e.g., en, de, es, fr, it, pt, ja, zh, ko, etc.) |
| `model_type` | String | No | "english" | Model type: "english" (English only) or "multilingual" (23 languages) |
| `emotion_intensity` | Number | No | 1.0 | Emotion exaggeration level (0.0 to 2.0) |
| `webhook_url` | String | No | - | URL to receive callback notification when processing is complete |
| `id` | String | No | - | Custom identifier for tracking the request |

### Supported Languages (Multilingual Model)

English (en), German (de), Spanish (es), French (fr), Italian (it), Portuguese (pt), Polish (pl), Turkish (tr), Russian (ru), Dutch (nl), Czech (cs), Arabic (ar), Chinese (zh), Japanese (ja), Korean (ko), Hungarian (hu), Hindi (hi), and more.

### Example Request

```json
{
  "text": "Hello! Welcome to our AI-powered text-to-speech service. This is a demonstration of Chatterbox TTS technology.",
  "language": "en",
  "model_type": "english",
  "emotion_intensity": 1.2,
  "webhook_url": "https://your-webhook-endpoint.com/callback",
  "id": "tts-request-123"
}
```

### Example Multilingual Request (German)

```json
{
  "text": "Guten Tag! Willkommen bei unserem KI-gestützten Text-zu-Sprache-Dienst.",
  "language": "de",
  "model_type": "multilingual",
  "emotion_intensity": 1.0,
  "webhook_url": "https://your-webhook-endpoint.com/callback",
  "id": "tts-german-123"
}
```

### Example cURL Command

```bash
curl -X POST \
  https://api.example.com/v1/chatterbox/text-to-speech \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: your-api-key-here' \
  -d '{
    "text": "Hello! This is a test of the text-to-speech system.",
    "language": "en",
    "model_type": "english",
    "emotion_intensity": 1.0,
    "webhook_url": "https://your-webhook-endpoint.com/callback",
    "id": "tts-request-123"
  }'
```

## Response

### Synchronous Response (No webhook_url provided)

If no `webhook_url` is provided, the request will be processed synchronously and return:

```json
{
  "code": 200,
  "id": "tts-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "https://storage.example.com/generated-speech.wav",
  "message": "success",
  "run_time": 1.234,
  "queue_time": 0,
  "total_time": 1.234,
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

### Asynchronous Response (webhook_url provided)

If a `webhook_url` is provided, the request will be queued for processing and immediately return:

```json
{
  "code": 202,
  "id": "tts-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "processing",
  "pid": 12345,
  "queue_id": 67890,
  "max_queue_length": "unlimited",
  "queue_length": 1,
  "build_number": "1.0.123"
}
```

When processing is complete, a webhook will be sent to the provided URL with the following payload:

```json
{
  "endpoint": "/v1/chatterbox/text-to-speech",
  "code": 200,
  "id": "tts-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "https://storage.example.com/generated-speech.wav",
  "message": "success",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 2.345,
  "queue_time": 0.123,
  "total_time": 2.468,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

### Error Responses

#### Invalid Request Format (400 Bad Request)

```json
{
  "code": 400,
  "id": null,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Invalid request: 'text' is a required property",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

#### Authentication Error (401 Unauthorized)

```json
{
  "code": 401,
  "message": "Invalid or missing API key",
  "build_number": "1.0.123"
}
```

#### Processing Error (500 Internal Server Error)

```json
{
  "code": 500,
  "id": "tts-request-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Failed to load Chatterbox model: CUDA out of memory",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

## Usage Notes

1. **Model Selection**:
   - Use `"english"` model for English-only content (faster, smaller)
   - Use `"multilingual"` model for any of the 23 supported languages

2. **Text Length**: Keep text between 1-5000 characters for optimal results

3. **Emotion Intensity**:
   - `0.0` = Neutral/monotone
   - `1.0` = Normal emotion
   - `2.0` = Maximum emotion exaggeration

4. **GPU Acceleration**: The service will automatically use CUDA if available, otherwise falls back to CPU

5. **Audio Output**: Generated audio is in WAV format at 24kHz sample rate

6. **Model Caching**: Models are cached after first load to improve subsequent request performance

## Performance Considerations

- **First Request**: Initial model loading may take 10-30 seconds
- **Subsequent Requests**: Typically complete in 1-3 seconds
- **GPU vs CPU**: GPU processing is 5-10x faster than CPU
- **Memory Requirements**:
  - English model: ~2GB RAM
  - Multilingual model: ~3GB RAM
  - GPU: Minimum 4GB VRAM recommended

## Best Practices

1. **Use Webhooks for Production**: Always use webhooks in production environments to avoid timeout issues

2. **Include Custom IDs**: Always include a custom `id` parameter to track requests

3. **Language Selection**: Ensure the `language` parameter matches the text language when using multilingual model

4. **Emotion Control**: Start with default emotion_intensity (1.0) and adjust based on results

5. **Text Preprocessing**:
   - Remove special characters that shouldn't be spoken
   - Use proper punctuation for natural pauses
   - Break very long texts into multiple requests

6. **Error Handling**: Implement retry logic with exponential backoff for 500 errors

## Common Issues

1. **CUDA Out of Memory**: Reduce concurrent requests or use CPU fallback
2. **Model Loading Timeout**: First request may take longer - use webhooks
3. **Garbled Audio**: Check language parameter matches text language
4. **Slow Generation**: Ensure GPU drivers are properly installed

## Related Endpoints

- `/v1/chatterbox/voice-cloning` - Generate speech with custom voice cloning

## Example Integration (Python)

```python
import requests
import time

API_URL = "https://api.example.com/v1/chatterbox/text-to-speech"
API_KEY = "your-api-key"

def generate_speech(text, language="en", webhook_url=None):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    payload = {
        "text": text,
        "language": language,
        "model_type": "multilingual",
        "emotion_intensity": 1.0,
        "id": f"request-{int(time.time())}"
    }

    if webhook_url:
        payload["webhook_url"] = webhook_url

    response = requests.post(API_URL, json=payload, headers=headers)
    return response.json()

# Synchronous usage
result = generate_speech("Hello World!", language="en")
if result["code"] == 200:
    audio_url = result["response"]
    print(f"Audio generated: {audio_url}")

# Asynchronous usage
result = generate_speech(
    "Hallo Welt!",
    language="de",
    webhook_url="https://your-app.com/webhook"
)
if result["code"] == 202:
    print(f"Job queued: {result['job_id']}")
```
