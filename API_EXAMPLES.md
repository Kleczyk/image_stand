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

**Nagraj audio i wyślij do transkrypcji:**

```bash
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"
```

**Odpowiedź sukcesu:**
```json
{
  "success": true,
  "text": "To jest transkrypcja nagranego audio.",
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

**Z tekstu:**
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

### Krok 1: Transkrypcja mowy na tekst

```bash
# Nagraj audio (w przeglądarce lub użyj istniejącego pliku)
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@my_recording.webm" > transcription.json

# Wyciągnij tekst
TRANSCRIPT=$(cat transcription.json | python3 -c "import sys,json; print(json.load(sys.stdin)['text'])")
echo "Transkrypcja: $TRANSCRIPT"
```

### Krok 2: Generowanie obrazu z transkrypcji

```bash
# Użyj transkrypcji jako prompt
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=$TRANSCRIPT" \
  -F "resolution=1K" \
  -F "aspect_ratio=1:1"
```

### Krok 3: Pobranie wygenerowanego obrazu

```bash
# Z odpowiedzi wyciągnij local_url i pobierz obraz
LOCAL_URL=$(curl -s -X POST http://localhost:8000/api/generate \
  -F "prompt=$TRANSCRIPT" | python3 -c "import sys,json; print(json.load(sys.stdin)['local_url'])")

# Pobierz obraz
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
        print(f"Transkrypcja: {result['text']}")
        return result['text']
    else:
        print(f"Błąd: {result['error']}")
        return None

# Użycie
transcription = transcribe_audio("recording.webm")
```

### Generowanie obrazu z transkrypcji

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
        print(f"Błąd: {result['error']}")
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
            console.log('Transkrypcja:', response.data.text);
            return response.data.text;
        } else {
            console.error('Błąd:', response.data.error);
            return null;
        }
    } catch (error) {
        console.error('Błąd requestu:', error.message);
        return null;
    }
}

// Użycie
transcribeAudio('recording.webm').then(transcription => {
    if (transcription) {
        console.log('Gotowa transkrypcja:', transcription);
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
# Powinno zwrócić błąd (oczekiwane)
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@/dev/null" | python3 -m json.tool
```

### Test z przykładowym audio

```bash
# Jeśli masz plik audio
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@test_audio.webm" | python3 -m json.tool
```

## Troubleshooting

### Błąd: "OpenRouter API key not configured"

**Rozwiązanie:**
1. Sprawdź czy `OPENROUTER_API_KEY` jest ustawiony w `.env`
2. Restart kontenera: `docker compose restart api`
3. Sprawdź w kontenerze: `docker compose exec api env | grep OPENROUTER`

### Błąd: "Audio file is empty"

**Rozwiązanie:**
- Upewnij się, że plik audio istnieje i nie jest pusty
- Sprawdź format pliku (WebM, WAV, MP3, OGG)

### Błąd: "Unsupported audio format"

**Rozwiązanie:**
- Użyj obsługiwanego formatu: WebM, WAV, MP3, OGG
- Sprawdź MIME type pliku

### Timeout przy transkrypcji

**Rozwiązanie:**
- Sprawdź połączenie z OpenRouter.ai
- Sprawdź czy klucz API jest poprawny
- Sprawdź logi: `docker compose logs api`

