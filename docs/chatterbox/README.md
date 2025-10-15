# Chatterbox TTS Integration

**Author:** NetzPrinz aka Oliver Hees
**Based on:** no-code-architects-toolkit by Stephen G. Pope
**TTS Engine:** Chatterbox by Resemble AI

## Overview

This integration adds advanced Text-to-Speech (TTS) and Voice Cloning capabilities to the AI Toolkit using the Chatterbox TTS model by Resemble AI. Chatterbox is a state-of-the-art, open-source TTS system with multilingual support and zero-shot voice cloning.

## Features

### Core Capabilities
- **Text-to-Speech**: Convert text to natural-sounding speech in 23 languages
- **Voice Cloning**: Clone any voice from a single audio sample
- **Multilingual Support**: English, German, Spanish, French, Italian, Portuguese, Polish, Turkish, Russian, Dutch, Czech, Arabic, Chinese, Japanese, Korean, Hungarian, Hindi, and more
- **Emotion Control**: Adjustable emotion intensity (0.0 - 2.0)
- **High Quality**: 0.5B parameter model trained on 0.5M hours of data
- **GPU Acceleration**: CUDA support for ultra-low latency
- **Watermarking**: All generated audio includes watermarking

### Technical Specifications
- **Model Size**: 0.5 billion parameters
- **Training Data**: 500,000 hours of cleaned audio
- **Output Format**: WAV at 24kHz sample rate
- **Languages**: 23 languages supported
- **Backbone**: Llama-based architecture

## API Endpoints

### 1. Text-to-Speech
**Endpoint:** `/v1/chatterbox/text-to-speech`

Convert text to speech with optional language and emotion control.

```bash
POST /v1/chatterbox/text-to-speech
{
  "text": "Your text here",
  "language": "en",
  "model_type": "english",
  "emotion_intensity": 1.0
}
```

**Documentation:** [text_to_speech.md](./text_to_speech.md)

### 2. Voice Cloning
**Endpoint:** `/v1/chatterbox/voice-cloning`

Generate speech with a cloned voice from a reference audio sample.

```bash
POST /v1/chatterbox/voice-cloning
{
  "text": "Your text here",
  "voice_audio_url": "https://example.com/reference.wav",
  "language": "en",
  "model_type": "multilingual"
}
```

**Documentation:** [voice_cloning.md](./voice_cloning.md)

## Quick Start

### Prerequisites

1. **Python 3.11+** required
2. **CUDA-compatible GPU** recommended (6GB+ VRAM)
3. **Dependencies installed** from requirements.txt

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# API Authentication
export API_KEY=your-secret-api-key

# Cloud Storage (S3 or Google Cloud Storage)
export STORAGE_TYPE=s3  # or 'gcs'
export S3_BUCKET=your-bucket-name
# ... (see main README for complete config)
```

3. Start the server:
```bash
python app.py
```

### First Request

Test the TTS endpoint:

```bash
curl -X POST http://localhost:8080/v1/chatterbox/text-to-speech \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "text": "Hello! This is a test of the Chatterbox TTS system.",
    "language": "en",
    "model_type": "english"
  }'
```

## Supported Languages

| Language | Code | Model |
|----------|------|-------|
| English | en | english, multilingual |
| German | de | multilingual |
| Spanish | es | multilingual |
| French | fr | multilingual |
| Italian | it | multilingual |
| Portuguese | pt | multilingual |
| Polish | pl | multilingual |
| Turkish | tr | multilingual |
| Russian | ru | multilingual |
| Dutch | nl | multilingual |
| Czech | cs | multilingual |
| Arabic | ar | multilingual |
| Chinese | zh | multilingual |
| Japanese | ja | multilingual |
| Korean | ko | multilingual |
| Hungarian | hu | multilingual |
| Hindi | hi | multilingual |
| And more... | - | multilingual |

## Model Selection

### English Model
- **Use Case**: English-only applications
- **Advantages**: Faster, smaller memory footprint (~2GB)
- **Performance**: Optimized for English pronunciation

### Multilingual Model
- **Use Case**: Multi-language applications or voice cloning
- **Advantages**: 23 languages, voice cloning support
- **Memory**: ~3-4GB RAM required

## Performance Benchmarks

### Text-to-Speech (GPU)
- First request: 10-30 seconds (model loading)
- Subsequent requests: 1-3 seconds
- 100-character text: ~1 second

### Voice Cloning (GPU)
- First request: 15-45 seconds (model loading + download)
- Subsequent requests: 2-5 seconds
- Processing includes reference audio download and voice analysis

### CPU vs GPU Performance
- GPU: 5-10x faster than CPU
- Minimum GPU: 4GB VRAM (English), 6GB VRAM (Multilingual)

## Usage Examples

### Python Client

```python
import requests

class ChatterboxClient:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }

    def text_to_speech(self, text, language="en", model="english"):
        endpoint = f"{self.api_url}/v1/chatterbox/text-to-speech"
        payload = {
            "text": text,
            "language": language,
            "model_type": model
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return response.json()

    def voice_clone(self, text, voice_url, language="en"):
        endpoint = f"{self.api_url}/v1/chatterbox/voice-cloning"
        payload = {
            "text": text,
            "voice_audio_url": voice_url,
            "language": language,
            "model_type": "multilingual"
        }
        response = requests.post(endpoint, json=payload, headers=self.headers)
        return response.json()

# Usage
client = ChatterboxClient("https://api.example.com", "your-api-key")

# Generate speech
result = client.text_to_speech("Hello World!", language="en")
print(f"Audio URL: {result['response']}")

# Clone voice
result = client.voice_clone(
    text="This is my cloned voice",
    voice_url="https://example.com/reference.wav",
    language="en"
)
print(f"Cloned audio URL: {result['response']}")
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

class ChatterboxClient {
  constructor(apiUrl, apiKey) {
    this.apiUrl = apiUrl;
    this.apiKey = apiKey;
  }

  async textToSpeech(text, language = 'en', modelType = 'english') {
    const response = await axios.post(
      `${this.apiUrl}/v1/chatterbox/text-to-speech`,
      {
        text,
        language,
        model_type: modelType
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.apiKey
        }
      }
    );
    return response.data;
  }

  async voiceClone(text, voiceAudioUrl, language = 'en') {
    const response = await axios.post(
      `${this.apiUrl}/v1/chatterbox/voice-cloning`,
      {
        text,
        voice_audio_url: voiceAudioUrl,
        language,
        model_type: 'multilingual'
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': this.apiKey
        }
      }
    );
    return response.data;
  }
}

// Usage
const client = new ChatterboxClient('https://api.example.com', 'your-api-key');

// Generate speech
client.textToSpeech('Hello World!', 'en')
  .then(result => console.log('Audio URL:', result.response))
  .catch(error => console.error('Error:', error));
```

## Best Practices

### 1. Use Webhooks for Production
Always use webhooks for production applications to avoid timeout issues:

```json
{
  "text": "Your text",
  "webhook_url": "https://your-app.com/webhook",
  "id": "unique-request-id"
}
```

### 2. Implement Error Handling
```python
def safe_tts_request(text, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = client.text_to_speech(text)
            if result["code"] == 200:
                return result["response"]
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 3. Cache Generated Audio
Store frequently used audio files to reduce API calls and costs:

```python
audio_cache = {}

def get_or_generate_audio(text, language):
    cache_key = f"{text}:{language}"
    if cache_key in audio_cache:
        return audio_cache[cache_key]

    result = client.text_to_speech(text, language)
    audio_url = result["response"]
    audio_cache[cache_key] = audio_url
    return audio_url
```

### 4. Reference Audio Quality
For voice cloning, use high-quality reference audio:
- 3-30 seconds of clear speech
- No background noise
- Single speaker only
- Clear articulation

## Troubleshooting

### Common Issues

1. **Model Loading Timeout**
   - First request takes longer (model download)
   - Use webhooks for first-time requests
   - Consider warm-up requests on server start

2. **CUDA Out of Memory**
   - Reduce concurrent requests
   - Use CPU fallback: Set `CUDA_VISIBLE_DEVICES=""`
   - Upgrade GPU or use larger instance

3. **Poor Voice Cloning Quality**
   - Check reference audio quality
   - Ensure audio contains only target voice
   - Try different reference segments
   - Verify language parameter matches

4. **Slow Performance**
   - Verify GPU is being used
   - Check CUDA installation
   - Monitor system resources
   - Consider GPU upgrade

### Debug Mode

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
python app.py
```

## System Requirements

### Minimum Requirements
- CPU: 4+ cores
- RAM: 8GB
- Storage: 10GB free
- Python: 3.11+

### Recommended Requirements
- CPU: 8+ cores
- RAM: 16GB
- GPU: 6GB+ VRAM (CUDA-compatible)
- Storage: 20GB+ free
- Python: 3.11+

## Contributing

This integration is part of the AI Toolkit by NetzPrinz aka Oliver Hees, based on the no-code-architects-toolkit by Stephen G. Pope.

For issues, improvements, or feature requests, please contact the maintainer.

## License

This integration follows the GNU General Public License v2.0, consistent with the base toolkit.

## Credits

- **Integration Developer:** NetzPrinz aka Oliver Hees
- **Base Toolkit:** Stephen G. Pope (no-code-architects-toolkit)
- **TTS Engine:** Resemble AI (Chatterbox)
- **Model:** Open-source Chatterbox TTS

## Related Resources

- [Chatterbox GitHub Repository](https://github.com/resemble-ai/chatterbox)
- [Text-to-Speech API Documentation](./text_to_speech.md)
- [Voice Cloning API Documentation](./voice_cloning.md)
- [Main AI Toolkit README](../../README.md)

## Support

For technical support or questions:
- Check the [troubleshooting section](#troubleshooting)
- Review the [API documentation](./text_to_speech.md)
- Ensure all dependencies are correctly installed
- Verify environment variables are properly configured
