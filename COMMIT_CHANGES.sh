#!/bin/bash
# 📝 Script to commit speech-to-text feature changes

set -e

echo "📦 Preparing commits for Speech-to-Text feature..."
echo ""

# Check if git user is configured
if ! git config user.name > /dev/null 2>&1; then
    echo "⚠️  Git user is not configured."
    echo "Set configuration (locally for this repo):"
    echo ""
    read -p "Enter your name: " GIT_NAME
    read -p "Enter your email: " GIT_EMAIL
    git config user.name "$GIT_NAME"
    git config user.email "$GIT_EMAIL"
    echo "✅ Git configured locally"
    echo ""
fi

# Reset staging area (in case something is already staged)
git reset

# Commit 1: Backend - Speech-to-Text endpoint
echo "📝 Commit 1: Backend - Speech-to-Text endpoint"
git add src/services/openrouter_client.py src/api/schemas.py src/config.py src/main.py
git commit -m "feat: add speech-to-text endpoint using OpenRouter.ai

- Add OpenRouter client service (openrouter_client.py)
- Add SpeechToTextResponse schema
- Extend Settings with openrouter_api_key
- Add POST /api/speech-to-text endpoint
- Support multiple audio formats (WebM, WAV, MP3, OGG)
- Use Google Gemini 2.0 Flash Lite model via OpenRouter"
echo "✅ Commit 1 completed"
echo ""

# Commit 2: Frontend - Speech-to-Text UI
echo "📝 Commit 2: Frontend - Speech-to-Text UI"
git add frontend/streamlit_app.py
git commit -m "feat: add speech-to-text UI in Streamlit frontend

- Add speech-to-text section with audio recording
- Add transcription display as text
- Integrate with speech-to-text API endpoint
- Add audio player for recorded audio
- Display transcription in styled text box"
echo "✅ Commit 2 completed"
echo ""

# Commit 3: Configuration
echo "📝 Commit 3: Configuration"
git add env.example docker-compose.yml
git commit -m "config: add OpenRouter API key configuration

- Add OPENROUTER_API_KEY to env.example
- Add OPENROUTER_API_KEY to docker-compose.yml environment"
echo "✅ Commit 3 completed"
echo ""

# Commit 4: Documentation
echo "📝 Commit 4: Documentation"
git add README.md CHANGELOG.md API_EXAMPLES.md QUICK_START.md INSTALLATION.md DOCKER_INSTALLATION.md docker-commands.sh
git commit -m "docs: add comprehensive documentation for speech-to-text feature

- Update README.md with speech-to-text information
- Add CHANGELOG.md with feature summary
- Add API_EXAMPLES.md with usage examples
- Add QUICK_START.md for quick setup guide
- Update INSTALLATION.md with OpenRouter setup
- Add DOCKER_INSTALLATION.md for Docker setup
- Add docker-commands.sh helper script"
echo "✅ Commit 4 completed"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All commits completed successfully!"
echo ""
echo "📊 Last 5 commits:"
git log --oneline -5
echo ""
echo "💡 To push to remote:"
echo "   git push origin <branch-name>"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

