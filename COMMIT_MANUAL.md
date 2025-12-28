# 📝 Instrukcje commitowania zmian

## Automatyczne commitowanie

Start przygotowany skrypt:

```bash
./COMMIT_CHANGES.sh
```

Skrypt automatycznie:
1. Sprawdzi konfigurację git (i poprosi o dane if potrzeba)
2. Wykona 4 logiczne commity
3. Pokaże summary

## Ręczne commitowanie

If wolisz zrobić to ręcznie, wykonaj następujące commands:

### 1. Configuration git (tylko raz, if is not ustawiona)

```bash
git config user.name "Twoje Imię"
git config user.email "twoj@email.com"
```

### 2. Commit 1: Backend - Speech-to-Text endpoint

```bash
git add src/services/openrouter_client.py src/api/schemas.py src/config.py src/main.py
git commit -m "feat: add speech-to-text endpoint using OpenRouter.ai

- Add OpenRouter client service (openrouter_client.py)
- Add SpeechToTextResponse schema
- Extend Settings with openrouter_api_key
- Add POST /api/speech-to-text endpoint
- Support multiple audio formats (WebM, WAV, MP3, OGG)
- Use Google Gemini 2.0 Flash Lite model via OpenRouter"
```

### 3. Commit 2: Frontend - Speech-to-Text UI

```bash
git add frontend/streamlit_app.py
git commit -m "feat: add speech-to-text UI in Streamlit frontend

- Add speech-to-text section with audio recording
- Add transcription display as text
- Integrate with speech-to-text API endpoint
- Add audio player for recorded audio
- Display transcription in styled text box"
```

### 4. Commit 3: Configuration

```bash
git add env.example docker-compose.yml
git commit -m "config: add OpenRouter API key configuration

- Add OPENROUTER_API_KEY to env.example
- Add OPENROUTER_API_KEY to docker-compose.yml environment"
```

### 5. Commit 4: Documentation

```bash
git add README.md CHANGELOG.md API_EXAMPLES.md QUICK_START.md INSTALLATION.md DOCKER_INSTALLATION.md docker-commands.sh
git commit -m "docs: add comprehensive documentation for speech-to-text feature

- Update README.md with speech-to-text information
- Add CHANGELOG.md with feature summary
- Add API_EXAMPLES.md with usage examples
- Add QUICK_START.md for quick setup guide
- Update INSTALLATION.md with OpenRouter setup
- Add DOCKER_INSTALLATION.md for Docker setup
- Add docker-commands.sh helper script"
```

## Sprawdzenie commits

```bash
# See last commity
git log --oneline -5

# See szczegóły lastgo commita
git show HEAD

# See status
git status
```

## Wysyłanie to remote

```bash
# Check aktualny branch
git branch

# Wyślij commity
git push origin <nazwa-brancha>

# Lub if to pierwszy push
git push -u origin <nazwa-brancha>
```

## Konwencja commits

Używamy konwencji Conventional Commits:
- `feat:` - nowa funkcjonalność
- `fix:` - naprawa błędu
- `docs:` - zmiany w dokumentacji
- `config:` - zmiany w konfiguracji
- `refactor:` - refaktoryzacja kodu
- `Test:` - dodanie Testów

## Struktura commits

Każdy commit contains:
1. Krótki tytuł (max 50 znaków)
2. Pustą linię
3. Szczegółowy description zmian (bullet points)


