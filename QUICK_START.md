# ⚡ Szybki Start - Image Stand

## W 5 minut

### 1. Wymagania

- Docker i Docker Compose zainstalowane
- Dwa klucze API:
  - [kie.ai API Key](https://kie.ai) - do generowania obrazów
  - [OpenRouter.ai API Key](https://openrouter.ai) - do transkrypcji mowy

### 2. Konfiguracja

```bash
# Skopiuj plik konfiguracyjny
cp env.example .env

# Edytuj i dodaj klucze API
nano .env
```

Wypełnij w `.env`:
```env
KIE_API_KEY=sk-your-kie-api-key
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key
```

### 3. Uruchomienie

```bash
# Uruchom aplikację
docker compose up --build -d

# Sprawdź status
docker compose ps
```

### 4. Dostęp

- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000

### 5. Test

```bash
# Test health check
curl http://localhost:8000/api/health

# Powinno zwrócić:
# {"status":"ok","api_key_configured":true,"langgraph_enabled":true}
```

## Użycie - Speech-to-Text

### Przez interfejs webowy

1. Otwórz http://localhost:8501
2. Przejdź do sekcji "🎤 Speech-to-Text"
3. Kliknij mikrofon i nagraj audio
4. Kliknij "📝 Transkrybuj audio"
5. Skopiuj transkrypcję i wklej do pola prompt
6. Kliknij "🚀 Generate"

### Przez API

```bash
# Transkrypcja audio
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"

# Użyj transkrypcji do generowania obrazu
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=Twoja transkrypcja tutaj" \
  -F "resolution=1K"
```

## Przydatne komendy

```bash
# Restart aplikacji
docker compose restart

# Zatrzymaj
docker compose down

# Logi
docker compose logs -f

# Restart tylko API
docker compose restart api

# Restart tylko frontendu
docker compose restart frontend
```

## Rozwiązywanie problemów

### Porty zajęte?

Zmień w `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Zamiast 8000
  - "8502:8501"  # Zamiast 8501
```

### Błąd API key?

```bash
# Sprawdź .env
cat .env

# Sprawdź w kontenerze
docker compose exec api env | grep API_KEY

# Restart
docker compose restart api
```

### Kontenery nie startują?

```bash
# Sprawdź logi
docker compose logs

# Sprawdź status
docker compose ps -a
```

## Dokumentacja

- **Instalacja**: [INSTALLATION.md](INSTALLATION.md)
- **Przykłady API**: [API_EXAMPLES.md](API_EXAMPLES.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Docker**: [DOCKER_INSTALLATION.md](DOCKER_INSTALLATION.md)

## Szybki test endpointów

```bash
# 1. Health check
curl http://localhost:8000/api/health

# 2. Speech-to-text (wymaga pliku audio)
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"

# 3. Generate image
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=Test image" \
  -F "resolution=1K"
```

Gotowe! 🚀

