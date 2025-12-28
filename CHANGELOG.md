# 📝 Changelog - Speech-to-Text Feature

## Added Features

### 🎤 Speech-to-Text Endpoint

**New API endpoint:**
- `POST /api/speech-to-text` - Speech-to-text conversion

**Details:**
- Accepts audio files (WebM, WAV, MP3, OGG)
- Uses OpenRouter.ai API with Google Gemini 2.0 Flash Lite model
- Returns text transcription ready to use as prompt

**Usage example:**
```bash
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"
```

**Response:**
```json
{
  "success": true,
  "text": "Transcribed text...",
  "error": null
}
```

### 🎨 Frontend - Speech-to-Text Interface

**New section in Streamlit:**
- "🎤 Speech-to-Text" section with audio recording
- Display transcription as text
- Manual copy to prompt field capability

**Features:**
- Audio recording via browser microphone
- Audio player to listen to recording
- Transcription button
- Display transcription in readable format

## Technical Changes

### Backend

1. **New service:** `src/services/openrouter_client.py`
   - `transcribe_audio()` function for OpenRouter.ai communication
   - Support for various audio formats (WebM, WAV, MP3, OGG)
   - Audio to base64 conversion for API

2. **Extended configuration:** `src/config.py`
   - Added `openrouter_api_key` to Settings class
   - Loading from `OPENROUTER_API_KEY` environment variable

3. **New API schema:** `src/api/schemas.py`
   - `SpeechToTextResponse` - response schema for transcription

4. **New endpoint:** `src/main.py`
   - `POST /api/speech-to-text` with full validation
   - Error handling and various audio formats support

### Frontend

1. **New function:** `frontend/streamlit_app.py`
   - `speech_to_text()` - API endpoint call

2. **New UI section:**
   - "🎤 Speech-to-Text" section with recording
   - Display transcription in styled box
   - Integration with existing image generation interface

### Configuration

1. **Environment variables:**
   - `OPENROUTER_API_KEY` - OpenRouter.ai API key
   - Added to `env.example` and `docker-compose.yml`

## Requirements

- OpenRouter.ai API key (for speech-to-text)
- kie.ai API key (for image generation)

## Status

✅ API Endpoint - working
✅ OpenRouter.ai integration - working
✅ Frontend interface - working
⚠️ Automatic paste to prompt field - needs improvement (currently manual copying)

## Next Steps

- Improve automatic paste of transcription to prompt field
- Support more languages
- Transcription caching
- Transcription history
