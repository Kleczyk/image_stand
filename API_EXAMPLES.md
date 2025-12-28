# 📚 Przykłady użycia API

## Endpointy API

### 1. Health Check

```bash
curl http://localhost:8000/api/health
```

**Odpowiedź:**
```json
{
  "status": "ok",
  "api_key_configured": true,
  "langgraph_enabled": true
}
```

### 2. Speech-to-Text (Nowy!)

**Record audio and send for transcription:**

```bash
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"
```

**Odpowiedź sukcesu:**
```json
{
  "success": true,
  "text": "This is the transcription of the recorded audio.",
  "error": null
}
```

**Odpowiedź błędu:**
```json
{
  "success": false,
  "text": null,
  "error": "OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable."
}
```

**Obsługiwane formaty:**
- WebM (`audio/webm`)
- WAV (`audio/wav`)
- MP3 (`audio/mpeg`)
- OGG (`audio/ogg`)

### 3. Generowanie obrazu

**From text:**
```bash
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=A beautiful sunset over mountains" \
  -F "resolution=1K" \
  -F "aspect_ratio=16:9"
```

**Z edycją istniejącego obrazu:**
```bash
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=Add sunglasses and a hat" \
  -F "image_url=https://example.com/image.png"
```

**Odpowiedź:**
```json
{
  "success": true,
  "image_url": "https://kie.ai/...",
  "local_url": "/images/abc123.png",
  "task_id": "task_123",
  "state": "success",
  "error": null
}
```

### 4. Porównanie obrazów

```bash
curl -X POST http://localhost:8000/api/compare \
  -F "image1=@image1.png" \
  -F "image2=@image2.png"
```

**Odpowiedź:**
```json
{
  "success": true,
  "similarity_score": 0.85,
  "similarity_percentage": 85.0,
  "error": null
}
```

### 5. Ustawienie API Key

```bash
curl -X POST http://localhost:8000/api/key \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-api-key-here"}'
```

### 6. Status API Key

```bash
curl http://localhost:8000/api/key/status
```

## Kompletny przykład workflow

### Step 1: Speech-to-Text Transcription

```bash
# Record audio (in browser or use existing file)
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@my_recording.webm" > transcription.json

# Extract text
TRANSCRIPT=$(cat transcription.json | python3 -c "import sys,json; print(json.load(sys.stdin)['text'])")
echo "Transcription: $TRANSCRIPT"
```

### Step 2: Generate Image from Transcription

```bash
# Use transcription as prompt
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=$TRANSCRIPT" \
  -F "resolution=1K" \
  -F "aspect_ratio=1:1"
```

### Krok 3: Pobranie wygenerowanego obrazu

```bash
# Extract local_url from response and download image
LOCAL_URL=$(curl -s -X POST http://localhost:8000/api/generate \
  -F "prompt=$TRANSCRIPT" | python3 -c "import sys,json; print(json.load(sys.stdin)['local_url'])")

# Pull obraz
curl http://localhost:8000$LOCAL_URL -o generated_image.png
```

## Przykłady w Pythonie

### Transkrypcja audio

```python
import requests

def transcribe_audio(audio_file_path):
    url = "http://localhost:8000/api/speech-to-text"
    
    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        response = requests.post(url, files=files)
    
    result = response.json()
    
    if result['success']:
        print(f"Transcription: {result['text']}")
        return result['text']
    else:
        print(f"Error: {result['error']}")
        return None

# Usage
transcription = transcribe_audio("recording.webm")
```

### Generate Image from Transcription

```python
import requests

def generate_image_from_transcription(transcription):
    url = "http://localhost:8000/api/generate"
    
    data = {
        "prompt": transcription,
        "resolution": "1K",
        "aspect_ratio": "1:1",
        "output_format": "png"
    }
    
    response = requests.post(url, data=data)
    result = response.json()
    
    if result['success']:
        print(f"Obraz wygenerowany: {result['local_url']}")
        return result['local_url']
    else:
        print(f"Error: {result['error']}")
        return None

# Kompletny workflow
transcription = transcribe_audio("recording.webm")
if transcription:
    image_url = generate_image_from_transcription(transcription)
```

## Przykłady w JavaScript (Node.js)

### Transkrypcja audio

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function transcribeAudio(audioFilePath) {
    const form = new FormData();
    form.append('audio', fs.createReadStream(audioFilePath));
    
    try {
        const response = await axios.post(
            'http://localhost:8000/api/speech-to-text',
            form,
            { headers: form.getHeaders() }
        );
        
        if (response.data.success) {
            console.log('Transcription:', response.data.text);
            return response.data.text;
        } else {
            console.error('Error:', response.data.error);
            return null;
        }
    } catch (error) {
        console.error('Error requestu:', error.message);
        return null;
    }
}

// Usage
transcribeAudio('recording.webm').then(transcription => {
    if (transcription) {
        console.log('Ready transcription:', transcription);
    }
});
```

## Testowanie endpointów

### Test health check

```bash
# Powinno zwrócić status ok
curl http://localhost:8000/api/health | python3 -m json.tool
```

### Test speech-to-text z pustym plikiem

```bash
# Powinno zwrócić error (oczekiwane)
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@/dev/null" | python3 -m json.tool
```

### Test z przykładowym audio

```bash
# If masz plik audio
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@Test_audio.webm" | python3 -m json.tool
```

## Troubleshooting

### Error: "OpenRouter API key not configured"

**Rozwiązanie:**
1. Check if `OPENROUTER_API_KEY` is set in `.env`
2. Restart kontenera: `docker compose restart api`
3. Check in container: `docker compose exec api env | grep OPENROUTER`

### Error: "Audio file is empty"

**Rozwiązanie:**
- Ensure, że plik audio istnieje i is not pusty
- Check file format (WebM, WAV, MP3, OGG)

### Error: "Unsupported audio format"

**Rozwiązanie:**
- Use supported format: WebM, WAV, MP3, OGG
- Check file MIME type

### Timeout during transcription

**Solution:**
- Check connection to OpenRouter.ai
- Check if API key is correct
- Check logs: `docker compose logs api`

