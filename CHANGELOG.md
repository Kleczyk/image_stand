# 📝 Changelog - Speech-to-Text Feature

## Dodane funkcjonalności

### 🎤 Speech-to-Text Endpoint

**Nowy endpoint API:**
- `POST /api/speech-to-text` - Konwersja mowy na tekst

**Szczegóły:**
- Przyjmuje plik audio (WebM, WAV, MP3, OGG)
- Wykorzystuje OpenRouter.ai API z modelem Google Gemini 2.0 Flash Lite
- Zwraca transkrypcję tekstową gotową do użycia jako prompt

**Przykład użycia:**
```bash
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"
```

**Odpowiedź:**
```json
{
  "success": true,
  "text": "Transkrypcja tekstowa...",
  "error": null
}
```

### 🎨 Frontend - Speech-to-Text Interface

**Nowa sekcja w Streamlit:**
- Sekcja "🎤 Speech-to-Text" z nagrywaniem audio
- Wyświetlanie transkrypcji jako tekst
- Możliwość ręcznego kopiowania do pola prompt

**Funkcjonalności:**
- Nagrywanie audio przez mikrofon w przeglądarce
- Odtwarzacz audio do odsłuchania nagrania
- Przycisk transkrypcji
- Wyświetlanie transkrypcji w czytelnym formacie

## Zmiany techniczne

### Backend

1. **Nowy serwis:** `src/services/openrouter_client.py`
   - Funkcja `transcribe_audio()` do komunikacji z OpenRouter.ai
   - Obsługa różnych formatów audio (WebM, WAV, MP3, OGG)
   - Konwersja audio na base64 dla API

2. **Rozszerzona konfiguracja:** `src/config.py`
   - Dodano `openrouter_api_key` do klasy Settings
   - Wczytywanie z zmiennej środowiskowej `OPENROUTER_API_KEY`

3. **Nowy schemat API:** `src/api/schemas.py`
   - `SpeechToTextResponse` - schemat odpowiedzi dla transkrypcji

4. **Nowy endpoint:** `src/main.py`
   - `POST /api/speech-to-text` z pełną walidacją
   - Obsługa błędów i różnych formatów audio

### Frontend

1. **Nowa funkcja:** `frontend/streamlit_app.py`
   - `speech_to_text()` - wywołanie endpointu API

2. **Nowa sekcja UI:**
   - Sekcja "🎤 Speech-to-Text" z nagrywaniem
   - Wyświetlanie transkrypcji w stylizowanym boxie
   - Integracja z istniejącym interfejsem generowania obrazów

### Konfiguracja

1. **Zmienne środowiskowe:**
   - `OPENROUTER_API_KEY` - klucz API OpenRouter.ai
   - Dodano do `env.example` i `docker-compose.yml`

## Wymagania

- OpenRouter.ai API key (dla transkrypcji mowy)
- kie.ai API key (dla generowania obrazów)

## Status

✅ Endpoint API - działa
✅ Integracja z OpenRouter.ai - działa
✅ Frontend interface - działa
⚠️ Automatyczne wklejanie do pola prompt - wymaga poprawy (obecnie ręczne kopiowanie)

## Następne kroki

- Poprawa automatycznego wklejania transkrypcji do pola prompt
- Obsługa więcej języków
- Cache'owanie transkrypcji
- Historia transkrypcji

