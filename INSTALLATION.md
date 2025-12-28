# 🚀 Image Stand Installation Instructions

## Prerequisites

- **Docker** (version 20.10 or newer)
- **Docker Compose** (version 2.0 or newer)
- **API Keys**:
  - `KIE_API_KEY` - key from [kie.ai](https://kie.ai) (for image generation)
  - `OPENROUTER_API_KEY` - key from [OpenRouter.ai](https://openrouter.ai) (for speech-to-text)

## Step 1: Prepare API Keys

### 1.1. Get kie.ai API Key

1. Register at [kie.ai](https://kie.ai)
2. Go to API Keys section
3. Copy your API key

### 1.2. Get OpenRouter.ai API Key

1. Register at [OpenRouter.ai](https://openrouter.ai)
2. Go to [API Keys](https://openrouter.ai/keys) section
3. Create a new API key
4. Copy the API key

## Step 2: Configure Environment Variables

### Option A: `.env` file (recommended)

1. Copy example file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` file and add your keys:
   ```bash
   nano .env
   # or
   vim .env
   ```

3. Fill in values:
   ```env
   KIE_API_KEY=sk-your-kie-api-key-here
   OPENROUTER_API_KEY=sk-or-your-openrouter-api-key-here
   ```

### Option B: Export environment variables

```bash
export KIE_API_KEY="sk-your-kie-api-key-here"
export OPENROUTER_API_KEY="sk-or-your-openrouter-api-key-here"
```

## Step 3: Run Application

### 3.1. Build and start containers

```bash
# Build images and start containers
docker compose up --build
```

### 3.2. Run in background (detached mode)

```bash
# Run in background
docker compose up --build -d
```

### 3.3. Check container status

```bash
# Check if containers are running
docker compose ps
```

You should see:
```
NAME                  STATUS              PORTS
image-stand-api       Up                  0.0.0.0:8000->8000/tcp
image-stand-frontend   Up                  0.0.0.0:8501->8501/tcp
```

## Step 4: Verify Operation

### 4.1. Check API

Open in browser:
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/health
- **API Home**: http://localhost:8000

### 4.2. Check Frontend

Open in browser:
- **Streamlit Application**: http://localhost:8501

### 4.3. Test API (optional)

```bash
# Test health check
curl http://localhost:8000/api/health

# Test with API key (if set via .env)
curl -X POST http://localhost:8000/api/key \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-kie-api-key"}'
```

## Step 5: Using the Application

### 5.1. Via Web Interface (Streamlit)

1. Open http://localhost:8501
2. In sidebar:
   - Enter your `KIE_API_KEY` and click "Set API Key"
   - (Optional) Upload reference image
3. In "🎤 Speech-to-Text" section:
   - Click microphone button
   - Record your prompt
   - Click "📝 Transcribe Audio"
   - Copy transcription and paste into prompt field
4. Click "🚀 Generate" to generate image

### 5.2. Via API

```bash
# Generate image from text
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=A beautiful sunset over mountains" \
  -F "resolution=1K" \
  -F "aspect_ratio=16:9"

# Speech-to-text transcription
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"
```

## Useful Docker Compose Commands

### Stopping Application

```bash
# Stop containers
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Logs

```bash
# View logs from all services
docker compose logs

# View logs from API only
docker compose logs api

# View logs from frontend only
docker compose logs frontend

# Follow logs in real-time
docker compose logs -f
```

### Restart

```bash
# Restart all services
docker compose restart

# Restart API only
docker compose restart api

# Restart frontend only
docker compose restart frontend
```

### Rebuild

```bash
# Rebuild images (after code changes)
docker compose up --build

# Rebuild without cache
docker compose build --no-cache
docker compose up
```

### Check Status

```bash
# Container status
docker compose ps

# Resource usage
docker stats

# Check Docker network
docker network ls
```

## Troubleshooting

### Problem: Containers not starting

```bash
# Check error logs
docker compose logs

# Check if ports are free
netstat -tuln | grep -E '8000|8501'
# or
lsof -i :8000
lsof -i :8501
```

### Problem: "API key not configured" error

1. Check if `.env` exists and contains keys:
   ```bash
   cat .env
   ```

2. Check if variables are available in container:
   ```bash
   docker compose exec api env | grep API_KEY
   ```

3. If using exported variables, make sure they are available:
   ```bash
   echo $KIE_API_KEY
   echo $OPENROUTER_API_KEY
   ```

### Problem: Frontend cannot connect to API

1. Check if API is working:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. Check API logs:
   ```bash
   docker compose logs api
   ```

3. Check if containers are on the same network:
   ```bash
   docker network inspect image_stand_default
   ```

### Problem: Audio transcription error

1. Check if `OPENROUTER_API_KEY` is set:
   ```bash
   docker compose exec api env | grep OPENROUTER
   ```

2. Check API logs during transcription:
   ```bash
   docker compose logs -f api
   ```

3. Test endpoint directly:
   ```bash
   curl -X POST http://localhost:8000/api/speech-to-text \
     -F "audio=@Test_audio.webm"
   ```

### Problem: Images not being saved

1. Check if `images/` directory exists:
   ```bash
   ls -la images/
   ```

2. Check permissions:
   ```bash
   chmod 755 images/
   ```

3. Check API logs:
   ```bash
   docker compose logs api | grep -i image
   ```

## Update Application

```bash
# Stop containers
docker compose down

# Pull laTest changes (if using git)
git pull

# Rebuild and run
docker compose up --build -d
```

## Cleanup

```bash
# Remove containers, networks and volumes
docker compose down -v

# Remove unused images
docker image prune -a

# Remove everything (careful!)
docker system prune -a --volumes
```

## Ports

| Port | Service | Description |
|------|---------|-------------|
| 8000 | API | FastAPI backend |
| 8501 | Frontend | Streamlit application |

If ports are in use, you can change them in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
  - "8502:8501"  # Change 8501 to 8502
```

## Support

If you encounter problems:
1. Check logs: `docker compose logs`
2. Check status: `docker compose ps`
3. Check API documentation: http://localhost:8000/docs


