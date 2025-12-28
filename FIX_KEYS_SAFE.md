# 🔒 Bezpieczne removing keyy API z history git

## Problem

W history git są visible real API keys:
- `KIE_API_KEY=3bc7f2c018b971f67ebafa46937b34e9`
- `OPENROUTER_API_KEY=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`

## Rozwiązanie

### Opcja 1: Bezpieczne - Rewrite lastgo commita (if nie był pushowany)

If commit z keyami nie był jeszcze pushowany to remote:

```bash
# Naprain env.example (już zrobione)
git add env.example
git commit --amend --no-edit

# If to był ostatni commit, you can po prostu:
git commit --amend
```

### Opcja 2: Remove z całej history (requires force push)

**NOTE**: To will change history! Użyj tylko if:
- Repozytorium jest lokalne LUB
- Jesteś gotowy na force push LUB
- Masz backup

```bash
# 1. Backup
git branch backup-before-fix

# 2. Użyj skryptu
./REMOVE_KEYS_FROM_HISTORY.sh

# LUB ręcznie:
git filter-branch --force --tree-filter \
    "if [ -f env.example ]; then
        sed -i 's/3bc7f2c018b971f67ebafa46937b34e9/your_api_key_here/g' env.example
        sed -i 's/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/your_openrouter_api_key_here/g' env.example
    fi" \
    --prune-empty --tag-name-filter cat -- --all

# 3. Cleanup
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Opcja 3: Najbezpieczniejsza - Nowy commit z poprawką

If nie chcesz will changeać history:

```bash
# 1. Naprain env.example (już zrobione - ma placeholdery)
git add env.example
git commit -m "fix: remove real API keys from env.example

- Replace real keys with placeholders
- KIE_API_KEY: your_api_key_here
- OPENROUTER_API_KEY: your_openrouter_api_key_here"

# 2. IMPORTANT: Zrotate API keys w rzeczywistym użyciu!
#    - Generate nowe keys w kie.ai i OpenRouter.ai
#    - Update .env z nowymi keyami
```

## Sprawdzenie

```bash
# Check czy keys są jeszcze w history
git log --all --source -p | grep -E "3bc7f2c018b971f67ebafa46937b34e9|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"

# Check aktualny env.example
cat env.example | grep API_KEY
```

## IMPORTANT: Rotacja keyy

If keys były visible w history (szczególnie if były pushowane):

1. **Generate nowe keys**:
   - [kie.ai](https://kie.ai) - generate nowy KIE_API_KEY
   - [OpenRouter.ai](https://openrouter.ai) - generate nowy OPENROUTER_API_KEY

2. **Update .env** z nowymi keyami

3. **Remove stare keys** z platform (if możliwe)

## Zapobieganie w przyszłości

1. ✅ `.env` jest już w `.gitignore`
2. ✅ `env.example` contains tylko placeholdery
3. ⚠️  Zawsze sprawdzaj przed commitem: `git diff` i `git status`

## Sprawdzenie przed commitem

```bash
# Check co będzie commitowane
git diff --cached

# Check czy nie ma .env
git status

# Check czy nie ma keyy w zmianach
git diff | grep -E "sk-|API_KEY.*="
```

