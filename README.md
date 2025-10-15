# NetzPrinz AI Toolkit

**Author:** NetzPrinz aka Oliver Hees
**Based on:** [no-code-architects-toolkit](https://github.com/stephengpope/no-code-architects-toolkit) by Stephen G. Pope

---

## 🚀 Overview

The NetzPrinz AI Toolkit is an advanced, open-source API platform for media processing, text-to-speech, and voice cloning. Built on Python/Flask, it provides a comprehensive suite of tools for content creators, automation agencies, and AI developers.

### Key Features

- **🎙️ Chatterbox TTS Integration** - State-of-the-art text-to-speech in 23 languages
- **🔊 Voice Cloning** - Zero-shot voice cloning from single audio samples
- **🎬 Media Processing** - Audio, video, image conversion and manipulation
- **☁️ Cloud Storage** - S3, Google Cloud Storage, and local storage support
- **📊 Interactive API Docs** - Swagger UI for easy testing and exploration
- **🐳 Docker Ready** - Easy deployment with GPU support
- **⚡ High Performance** - GPU-accelerated processing, queue management
- **🔐 Secure** - API key authentication, rate limiting support

---

## 🎯 What Makes This Special?

### Chatterbox TTS (NEW!)
- **23 Languages**: en, de, es, fr, it, pt, pl, tr, ru, nl, cs, ar, zh, ja, ko, hu, hi, and more
- **Zero-Shot Voice Cloning**: Clone any voice from a 3-30 second audio sample
- **Emotion Control**: Adjustable emotion intensity (0.0 - 2.0)
- **High Quality**: 0.5B parameter model trained on 500k hours of data
- **GPU Accelerated**: 5-10x faster with NVIDIA GPU support
- **Cross-Lingual**: Clone voices and speak in different languages

### Media Processing
- Audio concatenation, conversion, and mixing
- Video captioning, trimming, splitting, and concatenation
- Image to video conversion
- FFmpeg composition with full control
- Media transcription and translation
- Metadata extraction

### Cloud Integration
- Amazon S3
- Google Cloud Storage
- Dropbox
- Google Drive
- Local storage

---

## 📖 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/your-username/ai-toolkit.git
cd ai-toolkit

# 2. Configure environment
cp .env.example .env
# Edit .env with your API_KEY and storage settings

# 3. Build and run (CPU-only)
docker-compose up -d

# 4. Or with GPU support (5-10x faster TTS)
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d

# 5. Access Swagger UI
open http://localhost:8080/api/docs
```

### Option 2: Local Development

```bash
# 1. Prerequisites
# - Python 3.11+
# - FFmpeg installed
# - Optional: CUDA for GPU support

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env

# 4. Run
python app.py

# 5. Access API
open http://localhost:8080/api/docs
```

---

## 🎙️ Chatterbox TTS Examples

### Text-to-Speech (English)

```bash
curl -X POST http://localhost:8080/v1/chatterbox/text-to-speech \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "text": "Hello! Welcome to the AI Toolkit.",
    "language": "en",
    "model_type": "english"
  }'
```

### Text-to-Speech (German)

```bash
curl -X POST http://localhost:8080/v1/chatterbox/text-to-speech \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "text": "Guten Tag! Willkommen beim AI Toolkit.",
    "language": "de",
    "model_type": "multilingual"
  }'
```

### Voice Cloning

```bash
curl -X POST http://localhost:8080/v1/chatterbox/voice-cloning \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "text": "This is my cloned voice speaking!",
    "voice_audio_url": "https://example.com/reference-voice.wav",
    "language": "en",
    "model_type": "multilingual"
  }'
```

---

## 📚 API Endpoints

### 🎙️ Chatterbox TTS (NEW!)

- **POST /v1/chatterbox/text-to-speech** - Generate speech from text ([Docs](docs/chatterbox/text_to_speech.md))
- **POST /v1/chatterbox/voice-cloning** - Clone voices and generate speech ([Docs](docs/chatterbox/voice_cloning.md))

### 🎵 Audio

- **POST /v1/audio/concatenate** - Combine multiple audio files

### 🎬 Video

- **POST /v1/video/caption** - Add captions to videos
- **POST /v1/video/concatenate** - Combine videos
- **POST /v1/video/cut** - Cut segments from videos
- **POST /v1/video/split** - Split videos into segments
- **POST /v1/video/trim** - Trim videos
- **POST /v1/video/thumbnail** - Extract thumbnails

### 🖼️ Image

- **POST /v1/image/convert/video** - Convert images to videos
- **POST /v1/image/screenshot/webpage** - Capture webpage screenshots

### 📁 Media

- **POST /v1/media/convert** - Convert media formats
- **POST /v1/media/transcribe** - Transcribe/translate media
- **POST /v1/media/metadata** - Extract metadata
- **POST /v1/media/silence** - Detect silence

### 🔧 FFmpeg

- **POST /v1/ffmpeg/compose** - Complex media processing

### 💾 Storage

- **POST /v1/s3/upload** - Upload to S3-compatible storage

### 🛠️ Toolkit

- **POST /v1/toolkit/authenticate** - Validate API keys
- **GET /v1/toolkit/test** - Test API functionality
- **GET /v1/toolkit/job/status** - Check job status

**👉 [Complete API Documentation](http://localhost:8080/api/docs)** (after starting server)

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```bash
# API Configuration
API_KEY=your-secret-api-key
API_HOST=localhost:8080

# Storage Configuration
STORAGE_TYPE=s3  # or 'gcs' or 'local'

# S3 Storage
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_REGION=us-east-1

# Google Cloud Storage
GCS_BUCKET=your-bucket-name
GCS_CREDENTIALS_JSON=path/to/credentials.json

# Local Storage
LOCAL_STORAGE_PATH=/app/storage

# Performance
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=300
MAX_QUEUE_LENGTH=100

# GPU Configuration (optional)
CUDA_VISIBLE_DEVICES=0  # GPU index
```

---

## 🐳 Docker Deployment

### CPU-Only

```bash
docker-compose up -d
```

### With GPU Support

```bash
# Prerequisites: nvidia-docker2
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

### Verify GPU Access

```bash
docker-compose exec ncat nvidia-smi
```

**[📖 Complete Docker Guide](docs/docker-deployment.md)**

---

## 🌐 Cloud Deployment

### Digital Ocean
- [Digital Ocean Deployment Guide](docs/cloud-installation/do.md)

### Google Cloud Run
- [GCP Deployment Guide](docs/cloud-installation/gcp.md)

### AWS, Azure, etc.
- Use standard Docker deployment
- See [Docker Guide](docs/docker-deployment.md)

---

## 📊 Swagger UI

Access interactive API documentation:

```
http://localhost:8080/api/docs
```

Features:
- Try out endpoints directly in browser
- API key authentication
- Request/response examples
- Schema validation
- Export OpenAPI spec

**[📖 Swagger Documentation](docs/swagger.md)**

---

## 🔧 System Requirements

### Minimum (CPU-only)
- **CPU**: 4+ cores
- **RAM**: 8GB
- **Storage**: 10GB free
- **Python**: 3.11+

### Recommended (GPU)
- **CPU**: 8+ cores
- **RAM**: 16GB
- **GPU**: 6GB+ VRAM (NVIDIA CUDA)
- **Storage**: 20GB+ free
- **Python**: 3.11+

---

## 📈 Performance

### Text-to-Speech (Chatterbox)

| Configuration | First Request | Subsequent |
|--------------|---------------|------------|
| CPU-only | 10-30s (model load) | 3-8s |
| GPU (4GB+ VRAM) | 15-30s (model load) | 1-3s |

### Media Processing

Depends on file size and operation. Use webhooks for async processing.

---

## 🛠️ Development

### Adding New Endpoints

1. Create route file: `routes/v1/category/action.py`
2. Create service: `services/v1/category/action.py`
3. Add Swagger documentation
4. Restart server

**[📖 Adding Routes Guide](docs/adding_routes.md)**

### Testing

```bash
# Run tests
pytest

# Check API health
curl http://localhost:8080/v1/toolkit/test
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

---

## 📄 License

This project is licensed under the [GNU General Public License v2.0 (GPL-2.0)](LICENSE).

Based on [no-code-architects-toolkit](https://github.com/stephengpope/no-code-architects-toolkit) by Stephen G. Pope.

---

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **Chatterbox TTS**: [docs/chatterbox/](docs/chatterbox/)
- **Docker Guide**: [docs/docker-deployment.md](docs/docker-deployment.md)
- **Swagger Docs**: [docs/swagger.md](docs/swagger.md)
- **Original Project**: [no-code-architects-toolkit](https://github.com/stephengpope/no-code-architects-toolkit)

---

## 🌟 Features Overview

```
✅ Text-to-Speech (23 languages)
✅ Voice Cloning (zero-shot)
✅ Audio/Video Processing
✅ Image Processing
✅ FFmpeg Integration
✅ Cloud Storage (S3, GCS)
✅ Swagger UI
✅ Docker Ready
✅ GPU Acceleration
✅ Webhook Support
✅ Queue Management
✅ API Authentication
✅ Comprehensive Documentation
```

---

**Made with ❤️ by NetzPrinz aka Oliver Hees**

**Based on the excellent work by Stephen G. Pope**
