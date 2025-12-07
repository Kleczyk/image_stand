# 🖼️ Image Stand

Image generation game and API using [kie.ai Nano Banana Pro](https://kie.ai/nano-banana-pro).

**Try to recreate a reference image using text prompts!** The system compares your generated images with the reference using SSIM similarity scoring.

## Features

- 🎨 **Text-to-Image**: Generate images from text prompts
- ✨ **Image Editing**: Edit generated images with additional prompts
- 📊 **Image Comparison**: Compare images using SSIM algorithm (similarity score)
- 🎮 **Game Mode**: Try to recreate a reference image and improve your score
- 💾 **Local Storage**: Images saved locally in Docker volume

## Tech Stack

- **Backend**: FastAPI + LangGraph
- **Frontend**: Streamlit
- **Image API**: kie.ai Nano Banana Pro
- **Container**: Docker + uv

## Quick Start

### 1. Get API Key

Get your API key from [kie.ai](https://kie.ai)

### 2. Run with Docker

```bash
# Clone and start
git clone <repo-url>
cd image_stand
docker compose up --build
```

### 3. Access

| Service | URL |
|---------|-----|
| **Frontend (Game)** | http://localhost:8501 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API** | http://localhost:8000 |

### 4. Play the Game

1. Open http://localhost:8501
2. Enter your kie.ai API key in the sidebar
3. Upload a reference image
4. Write a prompt to generate a similar image
5. See your similarity score!
6. Edit your image to improve the score

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/generate` | Generate/edit image |
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

## Project Structure

```
image_stand/
├── src/
│   ├── api/schemas.py          # Pydantic models
│   ├── graphs/
│   │   ├── image_generation.py # LangGraph generation workflow
│   │   └── image_comparison.py # LangGraph comparison workflow
│   ├── services/
│   │   ├── kie_client.py       # kie.ai API client
│   │   ├── comparison.py       # SSIM comparison
│   │   └── image_storage.py    # Local image storage
│   ├── config.py
│   └── main.py                 # FastAPI app
├── frontend/
│   ├── streamlit_app.py        # Streamlit game UI
│   └── Dockerfile
├── docker-compose.yml
├── Dockerfile
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

## License

MIT
