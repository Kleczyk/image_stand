# 🔒 Naprawa keyy API w history - Instrukcje

## Problem

Commit `61dacb5` contains real API keys w `env.example`:
- `KIE_API_KEY=3bc7f2c018b971f67ebafa46937b34e9`
- `OPENROUTER_API_KEY=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`

## Rozwiązanie: Interactive Rebase

### Krok 1: Rozpocznij rebase

```bash
git rebase -i 61dacb5^
```

### Krok 2: W edytorze

Change linię z commitem `61dacb5`:
```
pick 61dacb5 config: add OpenRouter API key configuration
```

Na:
```
edit 61dacb5 config: add OpenRouter API key configuration
```

Zapisz i zamknij edytor.

### Krok 3: Napraw plik

```bash
# Plik env.example jest już naprawiony (ma placeholdery)
git add env.example
git commit --amend --no-edit
```

### Krok 4: Kontynuuj rebase

```bash
git rebase --continue
```

### Krok 5: Force push (if był pushowany)

**NOTE**: To will change history to remote!

```bash
# Check czy ktoś inny nie pracuje nad tym
git fetch origin
git log origin/main..HEAD

# If jesteś pewien, że nikt inny nie pracuje:
git push --force-with-lease origin main
```

## Alternatywa: Nowy commit (safer)

If nie chcesz will changeać history:

1. ✅ Nowy commit już został utworzony z poprawką
2. Zrotate API keys w rzeczywistym użyciu:
   - Generate nowe keys w kie.ai i OpenRouter.ai
   - Update `.env` z nowymi keyami
   - Remove stare keys z platform

## Sprawdzenie po naprawie

```bash
# Check czy keys są jeszcze w history
git log --all --source -p | grep -E "3bc7f2c018b971f67ebafa46937b34e9|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"

# Powinno zwrócić pusto (lub tylko w commitach przed naprawą)
```

## IMPORTANT: Rotacja keyy

Ponieważ keys były visible w history (i prawdopodobnie na GitHubie):

1. **Generate nowe keys**:
   - [kie.ai](https://kie.ai) → Settings → API Keys → Generate New
   - [OpenRouter.ai](https://openrouter.ai) → Keys → Create Key

2. **Update `.env`** z nowymi keyami

3. **Remove stare keys** z platform (if możliwe)

4. **Restart application**:
   ```bash
   docker compose restart api
   ```

