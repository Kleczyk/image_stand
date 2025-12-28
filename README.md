# 🖼️ Image Stand

Image generation game and API using [kie.ai Nano Banana Pro](https://kie.ai/nano-banana-pro) with **Speech-to-Text** functionality.

**Try to recreate a reference image using text prompts or voice commands!** The system compares your generated images with the reference using SSIM similarity scoring.

## Features

- 🎨 **Text-to-Image**: Generate images from text prompts
- 🎤 **Speech-to-Text**: Record audio and convert to text using Google Gemini 2.0 Flash Lite via OpenRouter.ai
- ✨ **Image Editing**: Edit generated images with additional prompts
- 📊 **Image Comparison**: Compare images using SSIM algorithm (similarity score)
- 🎮 **Game Mode**: Try to recreate a reference image and improve your score
- 💾 **Local Storage**: Images saved locally in Docker volume
- 🔄 **LangGraph Workflows**: Stateful graph-based processing

## Tech Stack

- **Backend**: FastAPI + LangGraph
- **Frontend**: Streamlit
- **Image API**: kie.ai Nano Banana Pro
- **Container**: Docker + uv

## ⚡ Quick Start

### 1. Get API Keys

- **kie.ai API Key**: Get from [kie.ai](https://kie.ai) (for image generation)
- **OpenRouter.ai API Key**: Get from [OpenRouter.ai](https://openrouter.ai) (for speech-to-text)

### 2. Configure Environment

```bash
# Copy example env file
cp env.example .env

# Edit .env and add your API keys
nano .env
```

Fill in:
```env
KIE_API_KEY=sk-your-kie-api-key-here
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key-here
```

### 3. Run with Docker

```bash
# Start application
docker compose up --build -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 4. Access Application

| Service | URL |
|---------|-----|
| **Frontend (Streamlit)** | http://localhost:8501 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API Health** | http://localhost:8000/api/health |

**Szczegółowe instrukcje**: See [INSTALLATION.md](INSTALLATION.md)  
**Przykłady API**: See [API_EXAMPLES.md](API_EXAMPLES.md)

### 3. Access

| Service | URL |
|---------|-----|
| **Frontend (Game)** | http://localhost:8501 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API** | http://localhost:8000 |

### 5. Play the Game

1. Open http://localhost:8501
2. Enter your kie.ai API key in the sidebar
3. Upload a reference image
4. **Option A**: Write a prompt to generate a similar image
5. **Option B**: 
   - Go to "🎤 Speech-to-Text" section
   - Record audio using the microphone button
   - Click "📝 Transkrybuj audio" to transcribe
   - Copy the transcription text
   - Paste it into "✏️ Enter Your Prompt" field
6. Click "🚀 Generate" to create the image
7. See your similarity score!
8. Edit your image to improve the score

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/generate` | Generate/edit image |
| POST | `/api/speech-to-text` | Convert audio to text (WebM, WAV, MP3) |
| POST | `/api/compare` | Compare two images (SSIM) |
| POST | `/api/key` | Set API key |
| GET | `/api/images` | List saved images |
| GET | `/images/{filename}` | Get saved image |

### Example: Generate Image

```bash
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=A cute cartoon dog" \
  -F "resolution=1K"
```

### Example: Edit Image

```bash
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=Add sunglasses" \
  -F "image_url=https://..." \
  -F "resolution=1K"
```

### Example: Compare Images

```bash
curl -X POST http://localhost:8000/api/compare \
  -F "image1=@image1.png" \
  -F "image2=@image2.png"
```

### Example: Speech-to-Text

```bash
# Transcribe audio file
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"

# Response:
# {
#   "success": true,
#   "text": "Transcribed text...",
#   "error": null
# }
```

**More przykładów**: See [API_EXAMPLES.md](API_EXAMPLES.md)

## Project Structure

```
image_stand/
├── src/
│   ├── api/
│   │   └── schemas.py          # Pydantic models (including SpeechToTextResponse)
│   ├── graphs/
│   │   ├── image_generation.py # LangGraph generation workflow
│   │   └── image_comparison.py # LangGraph comparison workflow
│   ├── services/
│   │   ├── kie_client.py       # kie.ai API client
│   │   ├── openrouter_client.py # OpenRouter.ai client (NEW - speech-to-text)
│   │   ├── comparison.py       # SSIM comparison
│   │   └── image_storage.py    # Local image storage
│   ├── config.py               # Settings (including OPENROUTER_API_KEY)
│   └── main.py                 # FastAPI app (with /api/speech-to-text endpoint)
├── frontend/
│   ├── streamlit_app.py        # Streamlit UI (with speech-to-text section)
│   └── Dockerfile
├── docker-compose.yml          # Docker config (with OPENROUTER_API_KEY)
├── Dockerfile
├── env.example                 # Environment variables template
├── README.md                   # Main documentation
├── QUICK_START.md              # Quick start guide
├── INSTALLATION.md             # Detailed installation instructions
├── API_EXAMPLES.md             # API usage examples
├── CHANGELOG.md                # Changelog with new features
└── pyproject.toml
```

## Development

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Set API key
export KIE_API_KEY="your-key"

# Run API
uv run python -m src.main

# Run frontend (separate terminal)
uv run streamlit run frontend/streamlit_app.py
```

## Dokumentacja

- **Quick Start**: [QUICK_START.md](QUICK_START.md) - Szybki start w 5 minut
- **Instalacja**: [INSTALLATION.md](INSTALLATION.md) - Szczegółowe instrukcje instalacji
- **Przykłady API**: [API_EXAMPLES.md](API_EXAMPLES.md) - Przykłady użycia wszystkich endpointów
- **Changelog**: [CHANGELOG.md](CHANGELOG.md) - Lista zmian i nowych funkcji
- **Docker**: [DOCKER_INSTALLATION.md](DOCKER_INSTALLATION.md) - Instalacja Dockera

## License

MIT
