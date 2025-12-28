# 🖼️ Image Stand

Image generation game and API using [kie.ai Nano Banana Pro](https://kie.ai/nano-banana-pro) with **Speech-to-Text** functionality.

**Try to recreate a reference image using text prompts or voice commands!** The system compares your generated images with the reference using SSIM similarity scoring.

## ✨ Features

- 🎨 **Text-to-Image**: Generate images from text prompts
- 🎤 **Speech-to-Text**: Record audio and convert to text using Google Gemini 2.0 Flash Lite via OpenRouter.ai
- ✨ **Image Editing**: Edit generated images with additional prompts
- 📊 **Image Comparison**: Compare images using SSIM, CLIP embeddings, or hybrid method with non-linear scaling
- 🎮 **Game Mode**: Try to recreate a reference image and improve your score
- 💾 **Local Storage**: Images saved locally in Docker volume
- 🔄 **LangGraph Workflows**: Stateful graph-based processing

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- Two API keys:
  - [kie.ai API Key](https://kie.ai) - for image generation
  - [OpenRouter.ai API Key](https://openrouter.ai) - for speech-to-text

### Step 1: Get API Keys

1. **kie.ai API Key**: 
   - Sign up at [kie.ai](https://kie.ai)
   - Get your API key from the dashboard

2. **OpenRouter.ai API Key**:
   - Sign up at [OpenRouter.ai](https://openrouter.ai)
   - Create an API key at [OpenRouter Keys](https://openrouter.ai/keys)

### Step 2: Configure Environment

```bash
# Copy example environment file
cp env.example .env

# Edit .env and add your API keys
nano .env
# or use your preferred editor: vim, code, etc.
```

Add your keys to `.env`:
```env
KIE_API_KEY=sk-your-kie-api-key-here
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key-here
```

### Step 3: Start Application

```bash
# Build and start all services
docker compose up --build -d

# Check if containers are running
docker compose ps

# View logs (optional)
docker compose logs -f
```

### Step 4: Access Application

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8501 | Streamlit web interface |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **API Health** | http://localhost:8000/api/health | Health check endpoint |

### Step 5: Test It Works

```bash
# Test API health
curl http://localhost:8000/api/health

# Expected response:
# {"status":"ok","api_key_configured":true,"langgraph_enabled":true}
```

## 🎮 How to Use

### Via Web Interface

1. Open http://localhost:8501 in your browser
2. **Set API Key** (if not set in .env):
   - Enter your `KIE_API_KEY` in the sidebar
   - Click "Set API Key"
3. **Generate Image with Text**:
   - Enter your prompt in "✏️ Enter Your Prompt"
   - Click "🚀 Generate"
4. **Generate Image with Voice**:
   - Go to "🎤 Speech-to-Text" section
   - Click microphone button and record audio
   - Click "📝 Transcribe Audio"
   - Copy the transcribed text
   - Paste into "✏️ Enter Your Prompt" field
   - Click "🚀 Generate"

### Via API

See [API_EXAMPLES.md](API_EXAMPLES.md) for detailed examples.

**Quick examples:**

```bash
# Generate image
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=A cute cartoon dog" \
  -F "resolution=1K"

# Transcribe audio
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"
```

## 📚 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check and status |
| POST | `/api/generate` | Generate or edit image |
| POST | `/api/speech-to-text` | Convert audio to text (WebM, WAV, MP3, OGG) |
| POST | `/api/compare` | Compare two images (SSIM, embeddings, or hybrid method) |
| POST | `/api/key` | Set API key at runtime |
| GET | `/api/key/status` | Check API key status |
| POST | `/api/sensitivity` | Set similarity rigour/strictness (0.1-10.0) |
| GET | `/api/sensitivity` | Get current similarity rigour value |
| GET | `/api/images` | List all saved images |
| GET | `/images/{filename}` | Get saved image file |

### Image Comparison Endpoint

**POST `/api/compare`** - Compare two images for similarity

**Parameters:**
- `image1` (file, required): First image file
- `image2` (file, required): Second image file
- `method` (string, optional): Comparison method - `ssim`, `embeddings`, or `hybrid` (default: from config)
- `sensitivity` (float, optional): Rigour/strictness level (0.1-10.0, default: 1.0)
  - Higher values (2.0-5.0) = more strict = lower scores
  - Lower values (0.5-0.8) = more lenient = higher scores

**Response:**
```json
{
  "success": true,
  "similarity_score": 0.75,
  "similarity_percentage": 87.5,
  "method": "hybrid",
  "error": null
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/compare \
  -F "image1=@image1.png" \
  -F "image2=@image2.png" \
  -F "method=hybrid" \
  -F "sensitivity=3.0"
```

## 🎯 Similarity Thresholds and Configuration

The image comparison system uses **non-linear scaling** to better discriminate between different and similar images:

- **Completely different images** (e.g., can vs man): **5-10% similarity** (max 10%)
- **Somewhat similar images**: **20-50% similarity**
- **Similar images**: **60-90% similarity** (minimum 60%)
- **Very similar images**: **85-95% similarity**

### How It Works

The system uses piecewise linear scaling:
- Scores below `SIMILARITY_MIN_THRESHOLD` (default 0.3) → compressed to max 10%
- Scores above `SIMILARITY_MAX_THRESHOLD` (default 0.7) → expanded to 60%+
- Scores in between → gradual transition from 10% to 60%

### Configuration

Set these in your `.env` file:

```env
# Similarity algorithm
SIMILARITY_MODEL=hybrid  # Options: ssim, embeddings, hybrid

# Non-linear scaling (enabled by default)
SIMILARITY_USE_NONLINEAR=true  # Enable non-linear scaling
SIMILARITY_MIN_THRESHOLD=0.3   # Below this = different images (max 10%)
SIMILARITY_MAX_THRESHOLD=0.7   # Above this = similar images (60%+)

# Rigour/strictness
SIMILARITY_SENSITIVITY=1.0  # Higher = more strict (2.0-5.0), lower = more lenient (0.5-0.8)

# Hybrid method weights
SIMILARITY_EMBEDDING_WEIGHT=0.7  # Weight for CLIP embeddings (0.0-1.0)
SIMILARITY_SSIM_WEIGHT=0.3        # Weight for SSIM (0.0-1.0)
```

### Adjusting Similarity Rigour

**Via API:**
```bash
# Set strict mode (lower scores)
curl -X POST http://localhost:8000/api/sensitivity \
  -H "Content-Type: application/json" \
  -d '{"sensitivity": 3.0}'

# Check current value
curl http://localhost:8000/api/sensitivity
```

**Via Frontend:**
- Use the slider in the sidebar (0.1-10.0)
- Quick presets: "Lenient (0.5)", "Normal (1.0)", "Strict (3.0)"

**Sensitivity Values:**
- `0.5-0.8`: More lenient (higher scores)
- `1.0`: Normal (no adjustment)
- `2.0-3.0`: Strict (lower scores, good for strict comparison)
- `4.0-5.0`: Very strict (dramatically lower scores)

## 🛠️ Useful Commands

```bash
# Start application
docker compose up -d

# Stop application
docker compose down

# Restart application
docker compose restart

# View logs
docker compose logs -f

# View API logs only
docker compose logs -f api

# View frontend logs only
docker compose logs -f frontend

# Rebuild after code changes
docker compose up --build -d

# Check container status
docker compose ps
```

## 🔧 Troubleshooting

### API Key Not Working?

```bash
# 1. Check .env file exists and has keys
cat .env

# 2. Verify keys are loaded in container
docker compose exec api env | grep API_KEY

# 3. Restart API container
docker compose restart api

# 4. Check API logs for errors
docker compose logs api | grep -i error
```

### Ports Already in Use?

Edit `docker-compose.yml` and change ports:
```yaml
ports:
  - "8001:8000"  # Change API port to 8001
  - "8502:8501"  # Change frontend port to 8502
```

### Containers Not Starting?

```bash
# Check logs
docker compose logs

# Check container status
docker compose ps -a

# Rebuild from scratch
docker compose down
docker compose up --build -d
```

### Test API Connections

Use the comprehensive test script:
```bash
./test_api_connections.sh
```

This script tests:
- API health
- Environment variables
- Settings object
- OpenRouter API connection
- Speech-to-text endpoint
- .env file configuration

## 📖 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Quick start guide (5 minutes)
- **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation instructions
- **[API_EXAMPLES.md](API_EXAMPLES.md)** - Complete API usage examples
- **[CHANGELOG.md](CHANGELOG.md)** - Changelog and feature list
- **[DOCKER_INSTALLATION.md](DOCKER_INSTALLATION.md)** - Docker installation guide

## 🏗️ Tech Stack

- **Backend**: FastAPI + LangGraph
- **Frontend**: Streamlit
- **Image API**: kie.ai Nano Banana Pro
- **Speech-to-Text**: Google Gemini 2.0 Flash Lite via OpenRouter.ai
- **Container**: Docker + uv
- **Image Comparison**: SSIM, CLIP embeddings, or hybrid method with non-linear scaling

## 📁 Project Structure

```
image_stand/
├── src/
│   ├── api/
│   │   └── schemas.py          # API request/response models
│   ├── graphs/
│   │   ├── image_generation.py  # LangGraph generation workflow
│   │   └── image_comparison.py  # LangGraph comparison workflow
│   ├── services/
│   │   ├── kie_client.py       # kie.ai API client
│   │   ├── openrouter_client.py # OpenRouter.ai client (speech-to-text)
│   │   ├── comparison.py       # Image comparison (SSIM, embeddings, hybrid)
│   │   ├── image_embeddings.py # CLIP embeddings extraction
│   │   └── image_storage.py    # Local image storage
│   ├── config.py               # Application settings
│   └── main.py                 # FastAPI application
├── frontend/
│   ├── streamlit_app.py        # Streamlit web interface
│   └── Dockerfile
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # API container definition
├── env.example                 # Environment variables template
├── test_api_connections.sh     # API connection test script
└── README.md                   # This file
```

## 🧪 Development

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Set environment variables
export KIE_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"

# Run API
uv run python -m src.main

# Run frontend (in separate terminal)
uv run streamlit run frontend/streamlit_app.py
```

## 📄 License

MIT
