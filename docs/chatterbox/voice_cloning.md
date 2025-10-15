# Chatterbox Voice Cloning API Endpoint Documentation

**Author:** NetzPrinz aka Oliver Hees
**Integration:** Chatterbox TTS by Resemble AI

## Overview

The `/v1/chatterbox/voice-cloning` endpoint provides zero-shot voice cloning capabilities using the Chatterbox TTS model. This advanced feature allows you to generate speech in any voice by providing a reference audio sample. The endpoint supports multilingual voice cloning across 23 languages with emotion control and high-quality output.

### Key Features
- **Zero-Shot Voice Cloning**: Clone any voice from a single audio sample
- **Multilingual Support**: Clone voices across 23 different languages
- **Emotion Control**: Adjustable emotion intensity in cloned voice
- **High Fidelity**: Maintains voice characteristics and quality
- **Fast Processing**: GPU-accelerated for quick results

## Endpoint

- **URL**: `/v1/chatterbox/voice-cloning`
- **Method**: `POST`

## Request

### Headers

- `x-api-key`: Required. Your API authentication key.

### Body Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | String | Yes | - | Text to convert to speech with cloned voice (1-5000 characters) |
| `voice_audio_url` | String | Yes | - | URL of reference voice audio file for cloning (WAV, MP3, etc.) |
| `language` | String | No | "en" | Language code for the text (e.g., en, de, es, fr, it, pt, ja, zh, ko) |
| `model_type` | String | No | "multilingual" | Model type: "english" or "multilingual" |
| `emotion_intensity` | Number | No | 1.0 | Emotion exaggeration level (0.0 to 2.0) |
| `webhook_url` | String | No | - | URL to receive callback notification when processing is complete |
| `id` | String | No | - | Custom identifier for tracking the request |

### Reference Audio Requirements

- **Format**: WAV, MP3, FLAC, or other common audio formats
- **Duration**: 3-30 seconds recommended for best results
- **Quality**: Clear speech without background noise
- **Sample Rate**: Any (will be resampled to 24kHz internally)
- **Content**: Should contain only the target voice speaking

### Example Request

```json
{
  "text": "Hello! This is a demonstration of voice cloning technology. The voice you're hearing has been cloned from a reference audio sample.",
  "voice_audio_url": "https://example.com/reference-voice.wav",
  "language": "en",
  "model_type": "multilingual",
  "emotion_intensity": 1.0,
  "webhook_url": "https://your-webhook-endpoint.com/callback",
  "id": "voice-clone-123"
}
```

### Example Multilingual Request (Spanish Voice)

```json
{
  "text": "¡Hola! Esta es una demostración de la tecnología de clonación de voz.",
  "voice_audio_url": "https://example.com/spanish-voice-reference.mp3",
  "language": "es",
  "model_type": "multilingual",
  "emotion_intensity": 1.2,
  "webhook_url": "https://your-webhook-endpoint.com/callback",
  "id": "voice-clone-spanish-123"
}
```

### Example cURL Command

```bash
curl -X POST \
  https://api.example.com/v1/chatterbox/voice-cloning \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: your-api-key-here' \
  -d '{
    "text": "This is a test of voice cloning technology.",
    "voice_audio_url": "https://example.com/reference-voice.wav",
    "language": "en",
    "model_type": "multilingual",
    "emotion_intensity": 1.0,
    "webhook_url": "https://your-webhook-endpoint.com/callback",
    "id": "voice-clone-123"
  }'
```

## Response

### Synchronous Response (No webhook_url provided)

If no `webhook_url` is provided, the request will be processed synchronously and return:

```json
{
  "code": 200,
  "id": "voice-clone-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "https://storage.example.com/cloned-voice-audio.wav",
  "message": "success",
  "run_time": 3.456,
  "queue_time": 0,
  "total_time": 3.456,
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
  "id": "voice-clone-123",
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
  "endpoint": "/v1/chatterbox/voice-cloning",
  "code": 200,
  "id": "voice-clone-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "https://storage.example.com/cloned-voice-audio.wav",
  "message": "success",
  "pid": 12345,
  "queue_id": 67890,
  "run_time": 4.567,
  "queue_time": 0.234,
  "total_time": 4.801,
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
  "message": "Invalid request: 'voice_audio_url' is a required property",
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
  "id": "voice-clone-123",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Error downloading reference audio: Connection timeout",
  "pid": 12345,
  "queue_id": 67890,
  "queue_length": 0,
  "build_number": "1.0.123"
}
```

## Usage Notes

1. **Reference Audio Quality**:
   - Use clean, high-quality audio recordings
   - Avoid background noise, music, or multiple speakers
   - 3-30 seconds of speech is optimal
   - Clear articulation improves cloning accuracy

2. **Voice Cloning Accuracy**:
   - Better reference audio = better cloning results
   - Model captures tone, pitch, accent, and speaking style
   - Emotion and inflection are preserved from reference

3. **Language Matching**:
   - Reference audio language doesn't need to match target text language
   - Cross-lingual voice cloning is supported
   - Quality may vary with language combinations

4. **Processing Time**:
   - First request: 15-45 seconds (model loading)
   - Subsequent requests: 2-5 seconds
   - GPU acceleration significantly improves speed

5. **Audio Output**: Generated audio is in WAV format at 24kHz sample rate

## Performance Considerations

- **Download Time**: Reference audio download time adds to total processing time
- **File Size**: Keep reference audio files under 10MB for optimal performance
- **GPU Requirements**: Minimum 6GB VRAM recommended for multilingual model
- **Memory Usage**: ~3-4GB RAM required for voice cloning operations

## Best Practices

1. **Reference Audio Selection**:
   - Use professional voice recordings when possible
   - Ensure consistent volume levels
   - Remove silence at beginning and end
   - Use recordings in quiet environments

2. **Webhook Usage**: Always use webhooks for production due to processing time

3. **Custom IDs**: Include unique `id` parameters to track requests

4. **Error Handling**:
   - Implement retry logic for network-related errors
   - Validate reference audio URLs before submission
   - Handle timeout scenarios gracefully

5. **Voice Library Management**:
   - Cache frequently used reference audio URLs
   - Store generated audio URLs for reuse
   - Organize voices by use case or speaker

6. **Testing**:
   - Test with various voice types (male, female, different ages)
   - Verify quality across different languages
   - Check emotion intensity effects with your use case

## Security and Privacy

1. **Reference Audio Access**: Ensure reference audio URLs are publicly accessible or use temporary signed URLs
2. **Audio Rights**: Only use audio where you have proper rights and permissions
3. **Generated Content**: Be aware of deepfake implications and use responsibly
4. **Data Retention**: Generated audio is stored temporarily according to your storage configuration

## Common Issues

1. **Poor Cloning Quality**:
   - Check reference audio quality
   - Ensure audio contains only target voice
   - Try different reference audio segments

2. **Reference Audio Download Failures**:
   - Verify URL is accessible
   - Check audio file format compatibility
   - Ensure URL doesn't require authentication

3. **Language Mismatch**:
   - Verify language parameter matches text
   - Check reference audio language compatibility

4. **Slow Processing**:
   - Use GPU acceleration if available
   - Optimize reference audio file size
   - Use webhooks for asynchronous processing

## Use Cases

- **Content Creation**: Clone narrator voices for audiobooks or videos
- **Accessibility**: Generate personalized voices for assistive technology
- **Localization**: Maintain brand voice across multiple languages
- **Gaming**: Create unique character voices
- **Virtual Assistants**: Personalize AI assistant voices

## Related Endpoints

- `/v1/chatterbox/text-to-speech` - Standard text-to-speech without voice cloning

## Example Integration (Python)

```python
import requests
import time

API_URL = "https://api.example.com/v1/chatterbox/voice-cloning"
API_KEY = "your-api-key"

def clone_voice(text, voice_audio_url, language="en", webhook_url=None):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    payload = {
        "text": text,
        "voice_audio_url": voice_audio_url,
        "language": language,
        "model_type": "multilingual",
        "emotion_intensity": 1.0,
        "id": f"voice-clone-{int(time.time())}"
    }

    if webhook_url:
        payload["webhook_url"] = webhook_url

    response = requests.post(API_URL, json=payload, headers=headers)
    return response.json()

# Synchronous usage
result = clone_voice(
    text="Hello! This is my cloned voice speaking.",
    voice_audio_url="https://example.com/my-voice-reference.wav",
    language="en"
)

if result["code"] == 200:
    cloned_audio_url = result["response"]
    print(f"Voice cloned successfully: {cloned_audio_url}")

# Asynchronous usage with webhook
result = clone_voice(
    text="¡Hola! Esta es mi voz clonada hablando.",
    voice_audio_url="https://example.com/spanish-voice.mp3",
    language="es",
    webhook_url="https://your-app.com/webhook"
)

if result["code"] == 202:
    print(f"Voice cloning job queued: {result['job_id']}")
```

## Advanced Example: Voice Library Manager

```python
class VoiceLibrary:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.voices = {}

    def add_voice(self, name, reference_audio_url):
        """Add a voice to the library"""
        self.voices[name] = reference_audio_url

    def generate_speech(self, voice_name, text, language="en"):
        """Generate speech using a voice from the library"""
        if voice_name not in self.voices:
            raise ValueError(f"Voice '{voice_name}' not found in library")

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }

        payload = {
            "text": text,
            "voice_audio_url": self.voices[voice_name],
            "language": language,
            "model_type": "multilingual"
        }

        response = requests.post(
            f"{self.base_url}/v1/chatterbox/voice-cloning",
            json=payload,
            headers=headers
        )

        return response.json()

# Usage
library = VoiceLibrary(api_key="your-api-key", base_url="https://api.example.com")
library.add_voice("narrator", "https://example.com/narrator-voice.wav")
library.add_voice("character1", "https://example.com/character1-voice.wav")

# Generate speech with different voices
narrator_audio = library.generate_speech("narrator", "Once upon a time...", "en")
character_audio = library.generate_speech("character1", "Hello there!", "en")
```
