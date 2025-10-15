# Hostinger VPS - Quick Start

Die wichtigsten Befehle für schnelles Deployment auf Hostinger VPS.

## 🚀 Initial Deployment (5 Minuten)

```bash
# 1. Auf Server einloggen
ssh root@your-server-ip

# 2. Repository klonen
cd /opt
git clone https://github.com/your-username/ai-toolkit.git
cd ai-toolkit

# 3. Environment konfigurieren
cp .env.example .env
nano .env
# Setze mindestens: API_KEY, APP_DOMAIN, SSL_EMAIL

# 4. Build und Start (dauert 20-30 Min beim ersten Mal)
docker-compose build
docker-compose up -d

# 5. Testen
curl -X GET "http://localhost:8080/v1/toolkit/test" \
  -H "X-API-Key: your-api-key"
```

## 📝 Minimale .env Konfiguration

```bash
API_KEY=your-secret-api-key-here
APP_DOMAIN=your-domain.com
SSL_EMAIL=your-email@example.com
LOCAL_STORAGE_PATH=/app/storage
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=300
```

## 🔄 Updates deployen

```bash
cd /opt/ai-toolkit
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f ncat
```

## 🛠️ Wichtigste Befehle

```bash
# Logs anschauen
docker-compose logs -f ncat

# Container neu starten
docker-compose restart ncat

# Status prüfen
docker-compose ps

# Container stoppen
docker-compose stop

# In Container einloggen
docker-compose exec ncat /bin/bash

# Ressourcen überwachen
docker stats
```

## 🔥 Firewall öffnen

```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

## 🧪 API testen

```bash
# Lokaler Test
curl http://localhost:8080/v1/toolkit/test \
  -H "X-API-Key: your-api-key"

# Externer Test
curl http://your-server-ip:8080/v1/toolkit/test \
  -H "X-API-Key: your-api-key"

# Swagger UI
# Browser: http://your-server-ip:8080/api/docs
```

## 🔧 Troubleshooting

```bash
# Container läuft nicht?
docker-compose logs ncat

# Port belegt?
sudo lsof -i :8080
sudo kill -9 <PID>

# Zu wenig RAM?
free -h
docker stats

# FFmpeg Problem?
docker-compose exec ncat ffmpeg -version
```

## 📦 Neue Loop-Endpoints testen

```bash
# Audio Loop (5x)
curl -X POST http://localhost:8080/v1/audio/loop \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "audio_url": "https://example.com/audio.mp3",
    "loop_count": 5
  }'

# Video Loop (3x)
curl -X POST http://localhost:8080/v1/video/loop \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "loop_count": 3
  }'
```

## 🔐 Sicheren API-Key generieren

```bash
openssl rand -hex 32
```

## 💾 Backup

```bash
tar -czf backup-$(date +%Y%m%d).tar.gz .env storage/ logs/
```

## 📚 Vollständige Anleitung

Siehe: `docs/hostinger-deployment.md`

---

**Viel Erfolg beim Deployment! 🚀**
