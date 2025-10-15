# Hostinger VPS Deployment Guide

Schritt-für-Schritt Anleitung zur Deployment des NetzPrinz AI Toolkit auf einem Hostinger VPS mit nur Terminal-Zugang.

## Voraussetzungen

- Hostinger VPS mit Docker installiert
- SSH-Zugang zum Server
- Domain (optional, aber empfohlen für SSL)
- Git installiert auf dem Server

## Schritt 1: Repository auf Server klonen

```bash
# Mit SSH auf Server verbinden
ssh root@your-server-ip

# Ins gewünschte Verzeichnis wechseln (z.B. /opt)
cd /opt

# Repository klonen
git clone https://github.com/your-username/ai-toolkit.git
cd ai-toolkit
```

## Schritt 2: Environment-Variablen konfigurieren

```bash
# .env Datei aus Beispiel erstellen
cp .env.example .env

# .env Datei bearbeiten (mit nano oder vi)
nano .env
```

### Minimale Konfiguration für Start

```bash
# API Configuration
API_KEY=your-secret-api-key-here

# Domain (falls SSL gewünscht)
APP_DOMAIN=your-domain.com
SSL_EMAIL=your-email@example.com

# Storage Configuration - Wähle eine Option:

# Option 1: Lokaler Storage (einfachste Option für Start)
LOCAL_STORAGE_PATH=/app/storage

# Option 2: S3-Compatible Storage (z.B. DigitalOcean Spaces)
S3_ENDPOINT_URL=https://fra1.digitaloceanspaces.com
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET_NAME=your-bucket-name
S3_REGION=fra1

# Option 3: Google Cloud Storage
GCP_SA_CREDENTIALS=/path/to/credentials.json
GCP_BUCKET_NAME=your-bucket-name

# Performance Settings
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=300
MAX_QUEUE_LENGTH=100
```

**Wichtig:**
- Ersetze `your-secret-api-key-here` mit einem sicheren API-Schlüssel
- Für Production: Verwende S3 oder GCS statt lokalem Storage

Speichern mit `Ctrl+O`, Enter, dann `Ctrl+X`

## Schritt 3: Docker Images bauen

```bash
# Docker Image bauen (dauert ca. 20-30 Minuten beim ersten Mal)
docker build -t netzprinz/ai-toolkit:latest .

# Oder mit docker-compose
docker-compose build
```

**Tipp:** Der Build-Prozess kompiliert FFmpeg von Source, daher die lange Build-Zeit.

## Schritt 4: Deployment starten

### Option A: Mit Traefik (empfohlen für Production mit SSL)

```bash
# Mit Traefik für automatisches SSL
docker-compose up -d

# Logs anschauen
docker-compose logs -f ncat
```

### Option B: Ohne Traefik (nur HTTP, für Tests)

```bash
# docker-compose.simple.yml erstellen
cat > docker-compose.simple.yml <<EOF
services:
  ncat:
    image: netzprinz/ai-toolkit:latest
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env
    ports:
      - "8080:8080"
    volumes:
      - ./storage:/app/storage
      - ./logs:/app/logs
    restart: unless-stopped
EOF

# Starten
docker-compose -f docker-compose.simple.yml up -d

# Logs anschauen
docker-compose -f docker-compose.simple.yml logs -f ncat
```

## Schritt 5: Deployment verifizieren

```bash
# Test-Endpoint aufrufen (mit deinem API_KEY aus .env)
curl -X GET "http://localhost:8080/v1/toolkit/test" \
  -H "X-API-Key: your-secret-api-key-here"

# Erwartete Antwort:
# {"code": 200, "message": "success", "response": "API is working"}
```

**Bei externem Zugriff:**
```bash
# Ersetze localhost mit deiner Server-IP oder Domain
curl -X GET "http://your-server-ip:8080/v1/toolkit/test" \
  -H "X-API-Key: your-secret-api-key-here"
```

## Schritt 6: Swagger UI testen

Öffne im Browser:
```
http://your-server-ip:8080/api/docs
```

Oder mit Domain:
```
https://your-domain.com/api/docs
```

## Nützliche Docker-Befehle

```bash
# Logs in Echtzeit anschauen
docker-compose logs -f ncat

# Container neu starten
docker-compose restart ncat

# Container stoppen
docker-compose stop

# Container komplett entfernen und neu starten
docker-compose down
docker-compose up -d

# In Container einloggen (für Debugging)
docker-compose exec ncat /bin/bash

# Container-Ressourcen überwachen
docker stats

# Alle Logs anzeigen (auch von Traefik)
docker-compose logs -f
```

## Updates deployen

```bash
# Neueste Änderungen holen
cd /opt/ai-toolkit
git pull origin main

# Container neu bauen und starten
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Logs prüfen
docker-compose logs -f ncat
```

## Firewall-Konfiguration (falls aktiviert)

```bash
# Ports öffnen für HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Oder nur Port 8080 für direkten Zugriff
ufw allow 8080/tcp

# SSH nicht vergessen!
ufw allow 22/tcp

# Firewall aktivieren
ufw enable

# Status prüfen
ufw status
```

## Storage-Verzeichnisse

Bei lokalem Storage werden Dateien hier gespeichert:

```bash
# Im Container
/app/storage/          # Temporäre Dateien
/app/storage/jobs/     # Job-Status Dateien
/tmp/                  # Temp-Verzeichnis (wird automatisch bereinigt)

# Auf Host (gemounted)
./storage/
./logs/
```

## Troubleshooting

### Container startet nicht

```bash
# Logs prüfen
docker-compose logs ncat

# Häufige Probleme:
# 1. .env Datei fehlt oder fehlerhaft
# 2. API_KEY nicht gesetzt
# 3. Port 8080 bereits belegt
```

### Port bereits belegt

```bash
# Prüfen welcher Prozess Port 8080 nutzt
sudo lsof -i :8080

# Prozess beenden
sudo kill -9 <PID>

# Oder anderen Port in docker-compose.yml verwenden
```

### SSL-Zertifikate funktionieren nicht

```bash
# Traefik Logs prüfen
docker-compose logs traefik

# Sicherstellen dass:
# 1. Domain zeigt auf Server-IP
# 2. Ports 80 und 443 sind offen
# 3. SSL_EMAIL ist in .env gesetzt
# 4. APP_DOMAIN ist korrekt
```

### Zu wenig Speicher

```bash
# RAM-Nutzung prüfen
free -h

# Docker Container Ressourcen limitieren in docker-compose.yml:
services:
  ncat:
    # ... andere configs
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

### FFmpeg Fehler

```bash
# Prüfen ob FFmpeg im Container verfügbar ist
docker-compose exec ncat ffmpeg -version

# FFmpeg neu bauen falls nötig
docker-compose down
docker-compose build --no-cache ncat
docker-compose up -d
```

## Performance-Optimierung

### Mehr Worker

In `.env`:
```bash
GUNICORN_WORKERS=4  # Erhöhen für mehr parallel Requests
```

### Längere Timeouts

In `.env`:
```bash
GUNICORN_TIMEOUT=600  # Für große Video-Files
```

### Queue-Limits

In `.env`:
```bash
MAX_QUEUE_LENGTH=50  # Begrenzt gleichzeitige Jobs
```

## Backup-Strategie

```bash
# Regelmäßiges Backup der wichtigen Daten
tar -czf backup-$(date +%Y%m%d).tar.gz \
  .env \
  storage/ \
  logs/

# Backup an sicheren Ort kopieren
scp backup-*.tar.gz backup-server:/backups/
```

## Monitoring

```bash
# Docker Health Check hinzufügen in docker-compose.yml:
services:
  ncat:
    # ... andere configs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/v1/toolkit/test"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Security Best Practices

1. **Starken API-Key verwenden:**
   ```bash
   # Generieren mit:
   openssl rand -hex 32
   ```

2. **Firewall aktivieren** (siehe oben)

3. **Regelmäßige Updates:**
   ```bash
   apt update && apt upgrade -y
   docker-compose pull
   ```

4. **Logs überwachen:**
   ```bash
   # Verdächtige Aktivitäten prüfen
   docker-compose logs ncat | grep "401\|403\|500"
   ```

5. **Rate Limiting** (optional, via Traefik):
   Siehe `docker-compose.yml` für Traefik Middleware

## Nächste Schritte

Nach erfolgreichem Deployment:

1. ✅ API testen mit Swagger UI
2. ✅ Loop-Endpoints testen (`/v1/audio/loop`, `/v1/video/loop`)
3. ✅ Chatterbox TTS testen (falls benötigt)
4. ✅ Webhook-Integration testen
5. ✅ Monitoring einrichten
6. ✅ Backup-Routine etablieren

## Support

Bei Problemen:
- GitHub Issues: https://github.com/your-username/ai-toolkit/issues
- Logs prüfen: `docker-compose logs -f`
- Dokumentation: `/docs` Ordner im Repository

---

**Erstellt für Hostinger VPS Deployment**
