# ⚡ Quick Start - Image Stand

## Fastest way to start

### 1. Configure API keys

```bash
# Copy configuration file
cp env.example .env

# Edit and add your keys
nano .env
```

Fill in:
```env
KIE_API_KEY=sk-your-kie-api-key
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key
```

### 2. Start application

```bash
# Start everything
docker compose up --build -d
```

### 3. Open in browser

- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## Podstawowe polecenia

```bash
# Start
docker compose up --build -d

# Stop
docker compose down

# Logi
docker compose logs -f

# Status
docker compose ps

# Restart
docker compose restart
```

## Lub użyj skryptu pomocniczego

```bash
# Start
./docker-commands.sh start

# Stop
./docker-commands.sh stop

# Logi
./docker-commands.sh logs

# Status
./docker-commands.sh status

# Test API
./docker-commands.sh Test
```

## Test działania

```bash
# Check czy API działa
curl http://localhost:8000/api/health

# Powinno zwrócić:
# {"status":"ok","api_key_configured":true,"langgraph_enabled":true}
```

## Troubleshooting problems

### Ports in use?

Change porty w `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Instead of 8000
  - "8502:8501"  # Instead of 8501
```

### Error "API key not configured"?

1. Check `.env`:
   ```bash
   cat .env
   ```

2. Check w kontenerze:
   ```bash
   docker compose exec api env | grep API_KEY
   ```

3. Restart:
   ```bash
   docker compose restart
   ```

### Kontenery nie starting?

```bash
# Check logi
docker compose logs

# Check status
docker compose ps
```

## Pełna dokumentacja

See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.



