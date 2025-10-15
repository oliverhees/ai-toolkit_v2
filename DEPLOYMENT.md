# 🚀 Deployment Guide

**Author:** NetzPrinz aka Oliver Hees

## Push to GitHub

### 1. Create a New Repository on GitHub

Go to [GitHub](https://github.com/new) and create a new repository:
- Name: `ai-toolkit` (or your preferred name)
- Description: "Advanced AI Toolkit with TTS, Voice Cloning, and Media Processing"
- Public or Private (your choice)
- **DO NOT** initialize with README (we already have one)

### 2. Link Your Local Repository

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR-USERNAME/ai-toolkit.git

# Verify remote
git remote -v
```

### 3. Commit All Changes

```bash
# Check status
git status

# Add all files
git add .

# Create commit
git commit -m "feat: Add Chatterbox TTS integration

- Integrated Chatterbox TTS for 23-language text-to-speech
- Added voice cloning capability
- Implemented Swagger/OpenAPI documentation
- Updated Docker configuration for Python 3.11
- Added GPU support for accelerated processing
- Comprehensive documentation for all features

Based on no-code-architects-toolkit by Stephen G. Pope
Author: NetzPrinz aka Oliver Hees"

# Push to GitHub
git push -u origin main
```

### 4. Alternative: Using GitHub CLI

```bash
# Install gh CLI if not installed
# https://cli.github.com/

# Create repo and push
gh repo create ai-toolkit --public --source=. --remote=origin --push
```

---

## Docker Deployment Options

### Option A: Local Docker

```bash
# 1. Build image
docker-compose build

# 2. Start services
docker-compose up -d

# 3. Check logs
docker-compose logs -f
```

### Option B: Docker Hub

```bash
# 1. Tag image
docker tag netzprinz/ai-toolkit:latest YOUR-DOCKERHUB-USERNAME/ai-toolkit:latest

# 2. Push to Docker Hub
docker login
docker push YOUR-DOCKERHUB-USERNAME/ai-toolkit:latest

# 3. Use in production
# Update docker-compose.yml:
# image: YOUR-DOCKERHUB-USERNAME/ai-toolkit:latest
```

### Option C: GitHub Container Registry

```bash
# 1. Create GitHub Personal Access Token
# Settings → Developer settings → Personal access tokens → Tokens (classic)
# Scopes: write:packages, read:packages

# 2. Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR-USERNAME --password-stdin

# 3. Tag image
docker tag netzprinz/ai-toolkit:latest ghcr.io/YOUR-USERNAME/ai-toolkit:latest

# 4. Push to GHCR
docker push ghcr.io/YOUR-USERNAME/ai-toolkit:latest

# 5. Use in production
# Update docker-compose.yml:
# image: ghcr.io/YOUR-USERNAME/ai-toolkit:latest
```

---

## Cloud Deployment

### Digital Ocean App Platform

```bash
# 1. Push code to GitHub (see above)

# 2. Go to Digital Ocean
# https://cloud.digitalocean.com/apps

# 3. Click "Create App"

# 4. Connect GitHub repository

# 5. Configure:
# - Name: ai-toolkit
# - Region: Choose closest to you
# - Plan: Basic ($12/month) or Professional ($24/month+)

# 6. Environment Variables:
API_KEY=your-secret-key
STORAGE_TYPE=s3
S3_BUCKET=your-bucket
S3_ACCESS_KEY=your-key
S3_SECRET_KEY=your-secret
S3_REGION=nyc3
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=300

# 7. Deploy!
```

**[📖 Detailed DO Guide](docs/cloud-installation/do.md)**

### Google Cloud Run

```bash
# 1. Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# 2. Authenticate
gcloud auth login
gcloud config set project YOUR-PROJECT-ID

# 3. Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR-PROJECT-ID/ai-toolkit

# 4. Deploy to Cloud Run
gcloud run deploy ai-toolkit \
  --image gcr.io/YOUR-PROJECT-ID/ai-toolkit \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars="API_KEY=your-secret-key,STORAGE_TYPE=gcs,GCS_BUCKET=your-bucket"

# 5. Get URL
gcloud run services describe ai-toolkit --region us-central1
```

**[📖 Detailed GCP Guide](docs/cloud-installation/gcp.md)**

### AWS (ECS/Fargate)

```bash
# 1. Build for multi-platform
docker buildx build --platform linux/amd64,linux/arm64 \
  -t your-registry/ai-toolkit:latest --push .

# 2. Create ECS Task Definition
# Use AWS Console or CLI

# 3. Configure environment variables in Task Definition

# 4. Create ECS Service

# 5. Configure Application Load Balancer
```

### Hetzner Cloud

```bash
# 1. Create Hetzner Cloud Server
# https://console.hetzner.cloud/

# 2. SSH into server
ssh root@your-server-ip

# 3. Install Docker
curl -fsSL https://get.docker.com | sh

# 4. Clone repository
git clone https://github.com/YOUR-USERNAME/ai-toolkit.git
cd ai-toolkit

# 5. Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# 6. Deploy
docker-compose up -d

# 7. Configure domain (optional)
# Point your domain DNS to server IP
# Traefik will handle SSL automatically
```

---

## GPU Deployment

### Requirements
- NVIDIA GPU (6GB+ VRAM recommended)
- nvidia-docker2
- CUDA 11.8+

### Setup (Ubuntu/Debian)

```bash
# 1. Install NVIDIA drivers
sudo apt-get update
sudo apt-get install -y nvidia-driver-535

# 2. Install nvidia-docker2
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# 3. Test GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# 4. Deploy with GPU
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Check API health
curl https://your-domain.com/v1/toolkit/test

# Check Swagger UI
open https://your-domain.com/api/docs

# Test TTS endpoint
curl -X POST https://your-domain.com/v1/chatterbox/text-to-speech \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{"text": "Hello World!", "language": "en"}'
```

### 2. Monitor Logs

```bash
# Docker logs
docker-compose logs -f

# Specific service
docker-compose logs -f ncat

# Filter by time
docker-compose logs --since="1h"
```

### 3. Set Up Monitoring (Optional)

```bash
# Simple health check script
cat > health-check.sh << 'EOF'
#!/bin/bash
URL="https://your-domain.com/v1/toolkit/test"
if curl -s -f "$URL" > /dev/null; then
    echo "✅ API is healthy"
else
    echo "❌ API is down!"
    # Add notification here (email, Slack, etc.)
fi
EOF

chmod +x health-check.sh

# Add to crontab (every 5 minutes)
crontab -e
# Add line:
# */5 * * * * /path/to/health-check.sh
```

### 4. Backup Strategy

```bash
# Backup volumes
docker run --rm \
  -v ai-toolkit_storage:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/storage-backup-$(date +%Y%m%d).tar.gz -C /data .

# Automated backups (cron)
crontab -e
# Add line (daily at 2 AM):
# 0 2 * * * /path/to/backup-script.sh
```

---

## Updating

### Update Code

```bash
# 1. Pull latest changes
git pull origin main

# 2. Rebuild and restart
docker-compose build
docker-compose up -d

# 3. Check logs
docker-compose logs -f
```

### Rollback

```bash
# 1. Stop services
docker-compose down

# 2. Checkout previous version
git checkout <commit-hash>

# 3. Rebuild and start
docker-compose build
docker-compose up -d
```

---

## Troubleshooting

### Container won't start
```bash
docker-compose logs ncat
docker-compose down && docker-compose up
```

### Out of memory
```bash
# Increase memory limit in docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
```

### Slow performance
```bash
# Enable GPU or increase workers
GUNICORN_WORKERS=4
# Or add GPU support
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

---

## Security Checklist

- [ ] Change default API_KEY
- [ ] Use HTTPS (Traefik handles this)
- [ ] Firewall: Only ports 80, 443 open
- [ ] Regular security updates
- [ ] Monitor logs for abuse
- [ ] Implement rate limiting
- [ ] Use strong passwords/keys
- [ ] Regular backups
- [ ] Restrict Swagger UI in production

---

## Next Steps

1. ✅ Push to GitHub
2. ✅ Deploy to cloud
3. ✅ Configure domain
4. ✅ Test endpoints
5. ✅ Set up monitoring
6. ✅ Configure backups
7. 🚀 Start using!

---

**Made with ❤️ by NetzPrinz aka Oliver Hees**
