# 🚀 Instrukcja uruchomienia Image Stand

## Wymagania wstępne

- **Docker** (wersja 20.10 lub nowsza)
- **Docker Compose** (wersja 2.0 lub nowsza)
- **Klucze API**:
  - `KIE_API_KEY` - klucz z [kie.ai](https://kie.ai) (do generowania obrazów)
  - `OPENROUTER_API_KEY` - klucz z [OpenRouter.ai](https://openrouter.ai) (do transkrypcji mowy)

## Krok 1: Przygotowanie kluczy API

### 1.1. Uzyskaj klucz kie.ai API

1. Zarejestruj się na [kie.ai](https://kie.ai)
2. Przejdź do sekcji API Keys
3. Skopiuj swój klucz API

### 1.2. Uzyskaj klucz OpenRouter.ai API

1. Zarejestruj się na [OpenRouter.ai](https://openrouter.ai)
2. Przejdź do sekcji [API Keys](https://openrouter.ai/keys)
3. Utwórz nowy klucz API
4. Skopiuj klucz API

## Krok 2: Konfiguracja zmiennych środowiskowych

### Opcja A: Plik `.env` (zalecane)

1. Skopiuj plik przykładowy:
   ```bash
   cp env.example .env
   ```

2. Edytuj plik `.env` i wstaw swoje klucze:
   ```bash
   nano .env
   # lub
   vim .env
   ```

3. Wypełnij wartości:
   ```env
   KIE_API_KEY=sk-your-kie-api-key-here
   OPENROUTER_API_KEY=sk-or-your-openrouter-api-key-here
   ```

### Opcja B: Eksport zmiennych środowiskowych

```bash
export KIE_API_KEY="sk-your-kie-api-key-here"
export OPENROUTER_API_KEY="sk-or-your-openrouter-api-key-here"
```

## Krok 3: Uruchomienie aplikacji

### 3.1. Zbuduj i uruchom kontenery

```bash
# Zbuduj obrazy i uruchom kontenery
docker compose up --build
```

### 3.2. Uruchom w tle (detached mode)

```bash
# Uruchom w tle
docker compose up --build -d
```

### 3.3. Sprawdź status kontenerów

```bash
# Sprawdź czy kontenery działają
docker compose ps
```

Powinieneś zobaczyć:
```
NAME                  STATUS              PORTS
image-stand-api       Up                  0.0.0.0:8000->8000/tcp
image-stand-frontend   Up                  0.0.0.0:8501->8501/tcp
```

## Krok 4: Weryfikacja działania

### 4.1. Sprawdź API

Otwórz w przeglądarce:
- **API Dokumentacja (Swagger)**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/health
- **API Home**: http://localhost:8000

### 4.2. Sprawdź Frontend

Otwórz w przeglądarce:
- **Aplikacja Streamlit**: http://localhost:8501

### 4.3. Test API (opcjonalnie)

```bash
# Test health check
curl http://localhost:8000/api/health

# Test z kluczem API (jeśli ustawiony przez .env)
curl -X POST http://localhost:8000/api/key \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-kie-api-key"}'
```

## Krok 5: Użycie aplikacji

### 5.1. Przez interfejs webowy (Streamlit)

1. Otwórz http://localhost:8501
2. W sidebarze:
   - Wprowadź swój `KIE_API_KEY` i kliknij "Set API Key"
   - (Opcjonalnie) Prześlij obraz referencyjny
3. W sekcji "🎤 Record Audio (Speech-to-Text)":
   - Kliknij przycisk mikrofonu
   - Nagraj swój prompt
   - Kliknij "📝 Transcribe"
   - Transkrypcja automatycznie wypełni pole prompt
4. Kliknij "🚀 Generate" aby wygenerować obraz

### 5.2. Przez API

```bash
# Generuj obraz z tekstu
curl -X POST http://localhost:8000/api/generate \
  -F "prompt=A beautiful sunset over mountains" \
  -F "resolution=1K" \
  -F "aspect_ratio=16:9"

# Transkrypcja mowy na tekst
curl -X POST http://localhost:8000/api/speech-to-text \
  -F "audio=@recording.webm"
```

## Przydatne polecenia Docker Compose

### Zatrzymanie aplikacji

```bash
# Zatrzymaj kontenery
docker compose down

# Zatrzymaj i usuń wolumeny
docker compose down -v
```

### Logi

```bash
# Zobacz logi wszystkich serwisów
docker compose logs

# Zobacz logi tylko API
docker compose logs api

# Zobacz logi tylko frontendu
docker compose logs frontend

# Śledź logi na żywo
docker compose logs -f
```

### Restart

```bash
# Restart wszystkich serwisów
docker compose restart

# Restart tylko API
docker compose restart api

# Restart tylko frontendu
docker compose restart frontend
```

### Rebuild

```bash
# Przebuduj obrazy (po zmianach w kodzie)
docker compose up --build

# Przebuduj bez cache
docker compose build --no-cache
docker compose up
```

### Sprawdzenie statusu

```bash
# Status kontenerów
docker compose ps

# Użycie zasobów
docker stats

# Sprawdź sieć Docker
docker network ls
```

## Rozwiązywanie problemów

### Problem: Kontenery nie startują

```bash
# Sprawdź logi błędów
docker compose logs

# Sprawdź czy porty są wolne
netstat -tuln | grep -E '8000|8501'
# lub
lsof -i :8000
lsof -i :8501
```

### Problem: Błąd "API key not configured"

1. Sprawdź czy `.env` istnieje i zawiera klucze:
   ```bash
   cat .env
   ```

2. Sprawdź czy zmienne są dostępne w kontenerze:
   ```bash
   docker compose exec api env | grep API_KEY
   ```

3. Jeśli używasz eksportu zmiennych, upewnij się, że są dostępne:
   ```bash
   echo $KIE_API_KEY
   echo $OPENROUTER_API_KEY
   ```

### Problem: Frontend nie może połączyć się z API

1. Sprawdź czy API działa:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. Sprawdź logi API:
   ```bash
   docker compose logs api
   ```

3. Sprawdź czy kontenery są w tej samej sieci:
   ```bash
   docker network inspect image_stand_default
   ```

### Problem: Błąd transkrypcji audio

1. Sprawdź czy `OPENROUTER_API_KEY` jest ustawiony:
   ```bash
   docker compose exec api env | grep OPENROUTER
   ```

2. Sprawdź logi API podczas transkrypcji:
   ```bash
   docker compose logs -f api
   ```

3. Przetestuj endpoint bezpośrednio:
   ```bash
   curl -X POST http://localhost:8000/api/speech-to-text \
     -F "audio=@test_audio.webm"
   ```

### Problem: Obrazy nie są zapisywane

1. Sprawdź czy katalog `images/` istnieje:
   ```bash
   ls -la images/
   ```

2. Sprawdź uprawnienia:
   ```bash
   chmod 755 images/
   ```

3. Sprawdź logi API:
   ```bash
   docker compose logs api | grep -i image
   ```

## Aktualizacja aplikacji

```bash
# Zatrzymaj kontenery
docker compose down

# Pobierz najnowsze zmiany (jeśli używasz git)
git pull

# Przebuduj i uruchom
docker compose up --build -d
```

## Czyszczenie

```bash
# Usuń kontenery, sieci i wolumeny
docker compose down -v

# Usuń nieużywane obrazy
docker image prune -a

# Usuń wszystko (ostrożnie!)
docker system prune -a --volumes
```

## Porty

| Port | Serwis | Opis |
|------|--------|------|
| 8000 | API | FastAPI backend |
| 8501 | Frontend | Streamlit aplikacja |

Jeśli porty są zajęte, możesz je zmienić w `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Zmień 8000 na 8001
  - "8502:8501"  # Zmień 8501 na 8502
```

## Wsparcie

W razie problemów:
1. Sprawdź logi: `docker compose logs`
2. Sprawdź status: `docker compose ps`
3. Sprawdź dokumentację API: http://localhost:8000/docs


