# ⚡ Quick Start - Image Stand

## In 5 minutes

### 1. Requirements

- Docker and Docker Compose installed
- Two API keys:
  - [kie.ai API Key](https://kie.ai) - for image generation
  - [OpenRouter.ai API Key](https://openrouter.ai) - for speech-to-text

### 2. Configuration

```bash
# Copy configuration file
cp env.example .env

# Edit and add API keys
nano .env
```

Fill in `.env`:
```env
KIE_API_KEY=sk-your-kie-api-key
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key
```

### 3. Run

```bash
# Start application
docker compose up --build -d

# Check status
docker compose ps
```

### 4. Access

- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000

### 5. Test

```bash
# Test health check
curl http://localhost:8000/api/health

# Should return:
# {"status":"ok","api_key_configured":true,"langgraph_enabled":true}
```

## Usage - Speech-to-Text

### Via web interface

1. Open http://localhost:8501
2. Go to "🎤 Speech-to-Text" section
3. Click microphone and record audio
4. Click "📝 Transcribe Audio"
5. Copy transcription and paste into prompt field
6. Click "🚀 Generate"

### Via API

```bash
# Transcribe audio
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"

# Use transcription to generate image
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=Your transcription here" \
  -F "resolution=1K"
```

## Useful commands

```bash
# Restart application
docker compose restart

# Stop
docker compose down

# Logs
docker compose logs -f

# Restart only API
docker compose restart api

# Restart only frontend
docker compose restart frontend
```

## Troubleshooting

### Ports in use?

Change in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Instead of 8000
  - "8502:8501"  # Instead of 8501
```

### API key error?

```bash
# Check .env
cat .env

# Check in container
docker compose exec api env | grep API_KEY

# Restart
docker compose restart api
```

### Containers not starting?

```bash
# Check logs
docker compose logs

# Check status
docker compose ps -a
```

## Documentation

- **Installation**: [INSTALLATION.md](INSTALLATION.md)
- **API Examples**: [API_EXAMPLES.md](API_EXAMPLES.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Docker**: [DOCKER_INSTALLATION.md](DOCKER_INSTALLATION.md)

## Quick endpoint Tests

```bash
# 1. Health check
curl http://localhost:8000/api/health

# 2. Speech-to-text (requires audio file)
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"

# 3. Generate image
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=Test image" \
  -F "resolution=1K"
```

Gotowe! 🚀

