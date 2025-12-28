# ⚡ Quick Start - Image Stand

Get up and running in **5 minutes**!

## Prerequisites

- **Docker** and **Docker Compose** installed
  - [Install Docker](DOCKER_INSTALLATION.md) if needed
- Two API keys (get them now):
  - [kie.ai API Key](https://kie.ai) - for image generation
  - [OpenRouter.ai API Key](https://openrouter.ai) - for speech-to-text

## Step 1: Get API Keys (2 minutes)

### kie.ai API Key
1. Go to [kie.ai](https://kie.ai)
2. Sign up or log in
3. Get your API key from the dashboard

### OpenRouter.ai API Key
1. Go to [OpenRouter.ai](https://openrouter.ai)
2. Sign up or log in
3. Go to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Copy the key (starts with `sk-or-v1-...`)

## Step 2: Configure Environment (1 minute)

```bash
# Copy the example environment file
cp env.example .env

# Edit .env file with your API keys
nano .env
```

**Add your keys:**
```env
KIE_API_KEY=sk-your-kie-api-key-here
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key-here
```

**Save and exit** (Ctrl+X, then Y, then Enter in nano)

## Step 3: Start Application (1 minute)

```bash
# Build and start all services
docker compose up --build -d

# Wait a few seconds, then check status
docker compose ps
```

You should see both `image-stand-api` and `image-stand-frontend` containers running.

## Step 4: Access Application (30 seconds)

Open in your browser:

- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/api/health

## Step 5: Test It Works (30 seconds)

```bash
# Test API health
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{
  "status": "ok",
  "api_key_configured": true,
  "langgraph_enabled": true
}
```

✅ **If you see this, everything is working!**

## 🎮 Using the Application

### Generate Image with Text

1. Open http://localhost:8501
2. Enter your prompt: "A cute cartoon dog with blue eyes"
3. Click "🚀 Generate"
4. Wait ~30 seconds for the image to generate
5. View your image!

### Generate Image with Voice

1. Open http://localhost:8501
2. Scroll to "🎤 Speech-to-Text" section
3. Click the microphone button
4. Record your prompt (e.g., "A beautiful sunset over mountains")
5. Click "📝 Transcribe Audio"
6. Copy the transcribed text
7. Paste it into "✏️ Enter Your Prompt" field
8. Click "🚀 Generate"

## 🛠️ Common Commands

```bash
# Start application
docker compose up -d

# Stop application
docker compose down

# Restart application
docker compose restart

# View logs
docker compose logs -f

# Rebuild after changes
docker compose up --build -d

# Check status
docker compose ps
```

## 🔧 Quick Troubleshooting

### API key not working?

```bash
# Check .env file
cat .env

# Verify in container
docker compose exec api env | grep API_KEY

# Restart API
docker compose restart api
```

### Ports in use?

Change ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # API on 8001
  - "8502:8501"  # Frontend on 8502
```

### Containers not starting?

```bash
# Check logs
docker compose logs

# Rebuild
docker compose down
docker compose up --build -d
```

## 📚 Next Steps

- **Detailed Installation**: [INSTALLATION.md](INSTALLATION.md)
- **API Examples**: [API_EXAMPLES.md](API_EXAMPLES.md)
- **Test API Connections**: `./test_api_connections.sh`

## ✅ That's It!

You're ready to generate images with text or voice! 🚀

Need help? Check the [full documentation](README.md) or [troubleshooting guide](INSTALLATION.md#troubleshooting).
