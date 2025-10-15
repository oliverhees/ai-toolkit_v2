# Docker Deployment Guide

**Author:** NetzPrinz aka Oliver Hees
**Based on:** no-code-architects-toolkit by Stephen G. Pope

## Overview

This AI Toolkit can be deployed using Docker for easy, consistent deployment across different environments. The Docker setup includes:

- **Python 3.11** runtime
- **FFmpeg** with all codecs
- **Chatterbox TTS** for text-to-speech and voice cloning
- **GPU support** (optional) for accelerated TTS processing
- **Traefik** reverse proxy with automatic SSL
- **Persistent storage** for media files and logs

## Quick Start

### CPU-Only Deployment (Default)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd ai-toolkit

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Build and start
docker-compose up -d

# 4. Check logs
docker-compose logs -f ncat
```

### GPU-Enabled Deployment (Recommended for Chatterbox TTS)

```bash
# 1. Prerequisites
# - NVIDIA GPU with CUDA support
# - nvidia-docker2 installed

# 2. Build and start with GPU support
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d

# 3. Verify GPU access
docker-compose exec ncat nvidia-smi
```

## Prerequisites

### Required for All Deployments

- **Docker** 20.10 or higher
- **Docker Compose** v2.0 or higher
- **4GB+ RAM** (8GB+ recommended)
- **10GB+ disk space**

### Additional for GPU Support

- **NVIDIA GPU** with CUDA support
- **NVIDIA Docker Runtime** (nvidia-docker2)
- **CUDA 11.8+** drivers

#### Installing NVIDIA Docker (Ubuntu/Debian)

```bash
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-docker2
sudo apt-get update
sudo apt-get install -y nvidia-docker2

# Restart Docker daemon
sudo systemctl restart docker

# Test GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Configuration
API_KEY=your-secret-api-key-here
API_HOST=your-domain.com

# Storage Configuration
STORAGE_TYPE=s3  # or 'gcs' or 'local'

# S3 Storage (if STORAGE_TYPE=s3)
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_REGION=us-east-1
S3_ENDPOINT=  # Optional: for S3-compatible services

# Google Cloud Storage (if STORAGE_TYPE=gcs)
GCS_BUCKET=your-bucket-name
GCS_CREDENTIALS_JSON=path/to/credentials.json

# Local Storage (if STORAGE_TYPE=local)
LOCAL_STORAGE_PATH=/app/storage

# Traefik/SSL Configuration
APP_DOMAIN=api.your-domain.com
SSL_EMAIL=your-email@example.com

# Gunicorn Configuration
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=300

# Queue Configuration
MAX_QUEUE_LENGTH=100  # 0 for unlimited

# GPU Configuration (optional)
CUDA_VISIBLE_DEVICES=0  # GPU index, or empty for all GPUs
```

## Building the Image

### Build Locally

```bash
# CPU version
docker build -t netzprinz/ai-toolkit:latest .

# Check build
docker images | grep ai-toolkit
```

### Build Arguments

```bash
# Build with specific Python version
docker build --build-arg PYTHON_VERSION=3.11 -t netzprinz/ai-toolkit:latest .
```

## Deployment Options

### 1. Local Development

```yaml
# docker-compose.local.yml
services:
  ncat:
    image: netzprinz/ai-toolkit:latest
    build:
      context: .
    ports:
      - "8080:8080"
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
      # Mount code for hot-reload
      - ./app.py:/app/app.py
      - ./routes:/app/routes
      - ./services:/app/services
    environment:
      - API_KEY=dev-key
      - STORAGE_TYPE=local
      - LOCAL_STORAGE_PATH=/app/storage
```

```bash
docker-compose -f docker-compose.local.yml up
```

### 2. Production with Traefik (SSL)

```bash
# Uses docker-compose.yml
docker-compose up -d
```

Features:
- Automatic SSL via Let's Encrypt
- HTTPS redirect
- Domain-based routing

### 3. Production with GPU Support

```bash
# Combine standard and GPU configs
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

### 4. Custom Configuration

```bash
# Override specific settings
docker-compose -f docker-compose.yml -f docker-compose.custom.yml up -d
```

## Managing the Deployment

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d ncat

# View logs
docker-compose logs -f

# Follow specific service logs
docker-compose logs -f ncat
```

### Stopping Services

```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove with volumes (⚠️ deletes data)
docker-compose down -v
```

### Updating

```bash
# Pull latest code
git pull

# Rebuild image
docker-compose build

# Restart services
docker-compose up -d
```

### Scaling

```bash
# Run multiple workers (removes Traefik labels)
docker-compose up -d --scale ncat=3
```

## Monitoring

### Health Checks

```bash
# Check container status
docker-compose ps

# Check API health
curl http://localhost:8080/api/docs

# With API key
curl -H "x-api-key: your-key" http://localhost:8080/v1/chatterbox/text-to-speech
```

### Logs

```bash
# All logs
docker-compose logs

# Specific service
docker-compose logs ncat

# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Since timestamp
docker-compose logs --since="2024-01-01T00:00:00"
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

## GPU Support Details

### Verifying GPU Access

```bash
# Check GPU inside container
docker-compose exec ncat nvidia-smi

# Check PyTorch GPU access
docker-compose exec ncat python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Check Chatterbox GPU usage
docker-compose exec ncat python -c "from services.v1.chatterbox.tts import get_chatterbox_model; model = get_chatterbox_model()"
```

### GPU Configuration

Edit `docker-compose.gpu.yml`:

```yaml
# Use specific GPU
environment:
  - NVIDIA_VISIBLE_DEVICES=0  # First GPU only

# Use multiple GPUs
environment:
  - NVIDIA_VISIBLE_DEVICES=0,1  # First two GPUs
```

### GPU Memory Issues

If you encounter GPU out-of-memory errors:

1. **Reduce concurrent requests**:
```bash
# .env
GUNICORN_WORKERS=1
MAX_QUEUE_LENGTH=1
```

2. **Use CPU fallback**:
```bash
# Remove GPU configuration
docker-compose up -d  # Without gpu.yml
```

3. **Upgrade GPU**: Chatterbox requires 4GB+ VRAM (English), 6GB+ (Multilingual)

## Troubleshooting

### Common Issues

**1. Container won't start**
```bash
# Check logs
docker-compose logs ncat

# Check if port is in use
sudo lsof -i :8080

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

**2. "Permission denied" errors**
```bash
# Fix permissions
sudo chown -R 1000:1000 storage/ logs/

# Or run as root (not recommended)
docker-compose exec -u root ncat bash
```

**3. SSL certificate issues**
```bash
# Check Traefik logs
docker-compose logs traefik

# Verify DNS points to server
dig your-domain.com

# Check Let's Encrypt rate limits
# https://letsencrypt.org/docs/rate-limits/
```

**4. GPU not detected**
```bash
# Verify nvidia-docker2
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Check Docker daemon config
cat /etc/docker/daemon.json

# Should contain:
# {
#   "runtimes": {
#     "nvidia": {
#       "path": "nvidia-container-runtime",
#       "runtimeArgs": []
#     }
#   }
# }

# Restart Docker
sudo systemctl restart docker
```

**5. Slow TTS generation**
```bash
# Enable GPU support
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d

# Check if GPU is being used
docker-compose exec ncat nvidia-smi -l 1
```

**6. Out of disk space**
```bash
# Check disk usage
docker system df

# Clean up
docker system prune -a --volumes

# Remove old images
docker image prune -a
```

## Performance Optimization

### CPU-Only Deployment

```bash
# Adjust workers based on CPU cores
GUNICORN_WORKERS=4  # 2x CPU cores
GUNICORN_TIMEOUT=600  # Longer timeout for TTS

# Limit queue to prevent memory issues
MAX_QUEUE_LENGTH=10
```

### GPU Deployment

```bash
# Single worker per GPU (Chatterbox loads model per worker)
GUNICORN_WORKERS=1

# Allow longer processing time
GUNICORN_TIMEOUT=300

# Unlimited queue (GPU handles it fast)
MAX_QUEUE_LENGTH=0
```

### Production Best Practices

1. **Use webhooks** for all TTS requests (async processing)
2. **Enable GPU** for 5-10x faster TTS generation
3. **Monitor queue length** via API responses
4. **Set up health checks** for automatic restarts
5. **Use persistent volumes** for model caching
6. **Implement rate limiting** at reverse proxy level
7. **Regular backups** of storage volumes

## Security Considerations

### Production Checklist

- [ ] Change default API_KEY
- [ ] Use strong SSL certificate
- [ ] Enable firewall (only 80, 443 open)
- [ ] Regular security updates
- [ ] Monitor logs for abuse
- [ ] Implement rate limiting
- [ ] Use secrets management (not .env in production)
- [ ] Restrict Swagger UI access (/api/docs)
- [ ] Enable audit logging
- [ ] Regular backups

### Secure Secrets Management

```bash
# Use Docker secrets instead of .env
docker secret create api_key /path/to/api_key.txt

# Reference in docker-compose.yml
services:
  ncat:
    secrets:
      - api_key
    environment:
      - API_KEY_FILE=/run/secrets/api_key

secrets:
  api_key:
    external: true
```

## Backup and Restore

### Backup Volumes

```bash
# Backup storage
docker run --rm -v ai-toolkit_storage:/data -v $(pwd):/backup \
  alpine tar czf /backup/storage-backup.tar.gz -C /data .

# Backup logs
docker run --rm -v ai-toolkit_logs:/data -v $(pwd):/backup \
  alpine tar czf /backup/logs-backup.tar.gz -C /data .
```

### Restore Volumes

```bash
# Restore storage
docker run --rm -v ai-toolkit_storage:/data -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/storage-backup.tar.gz"
```

## Cloud Deployment

### Digital Ocean

See: [docs/cloud-installation/do.md](./cloud-installation/do.md)

### Google Cloud Run

See: [docs/cloud-installation/gcp.md](./cloud-installation/gcp.md)

### AWS ECS

```bash
# Build for multi-platform
docker buildx build --platform linux/amd64,linux/arm64 \
  -t your-registry/ai-toolkit:latest --push .

# Deploy to ECS
# (Use AWS Console or CLI to create ECS service)
```

## Related Documentation

- [Main README](../README.md)
- [Chatterbox TTS Integration](./chatterbox/README.md)
- [Swagger API Documentation](./swagger.md)
- [Adding New Routes](./adding_routes.md)

## Support

For Docker-related issues:
1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Test locally first: `docker-compose -f docker-compose.local.yml up`
4. Review this documentation
5. Check Docker and GPU requirements
