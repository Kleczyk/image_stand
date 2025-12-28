#!/bin/bash
# 🔍 Comprehensive API Connection Test Script
# Tests all API endpoints and connections

set -e

API_URL="http://localhost:8000/api"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     IMAGE STAND API - COMPREHENSIVE CONNECTION TEST        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Check if API is running
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 TEST 1: API Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API is running${NC}"
    curl -s "$API_URL/health" | python3 -m json.tool 2>/dev/null || curl -s "$API_URL/health"
else
    echo -e "${RED}❌ API is not running${NC}"
    echo "   Start with: docker compose up -d"
    exit 1
fi
echo ""

# Test 2: Check environment variables in container
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 TEST 2: Environment Variables in Container"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
KIE_KEY=$(docker compose exec -T api env | grep "^KIE_API_KEY=" | cut -d'=' -f2)
OPENROUTER_KEY=$(docker compose exec -T api env | grep "^OPENROUTER_API_KEY=" | cut -d'=' -f2)

if [ -n "$KIE_KEY" ] && [ "$KIE_KEY" != "" ]; then
    echo -e "${GREEN}✅ KIE_API_KEY is set (length: ${#KIE_KEY})${NC}"
else
    echo -e "${RED}❌ KIE_API_KEY is NOT set${NC}"
fi

if [ -n "$OPENROUTER_KEY" ] && [ "$OPENROUTER_KEY" != "" ]; then
    echo -e "${GREEN}✅ OPENROUTER_API_KEY is set (length: ${#OPENROUTER_KEY})${NC}"
else
    echo -e "${RED}❌ OPENROUTER_API_KEY is NOT set${NC}"
fi
echo ""

# Test 3: Check Settings object in Python
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 TEST 3: Settings Object in Python"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose exec -T api python3 << 'PYTHON_SCRIPT'
from src.config import settings
import os

print("Environment variables:")
kie_env = os.getenv("KIE_API_KEY", "")
openrouter_env = os.getenv("OPENROUTER_API_KEY", "")
print(f"  KIE_API_KEY from env: {'SET' if kie_env else 'NOT SET'} (length: {len(kie_env)})")
print(f"  OPENROUTER_API_KEY from env: {'SET' if openrouter_env else 'NOT SET'} (length: {len(openrouter_env)})")

print("\nSettings object:")
print(f"  settings.kie_api_key: {'SET' if settings.kie_api_key else 'NOT SET'} (length: {len(settings.kie_api_key)})")
print(f"  settings.openrouter_api_key: {'SET' if settings.openrouter_api_key else 'NOT SET'} (length: {len(settings.openrouter_api_key)})")

if not settings.openrouter_api_key:
    print("\n⚠️  WARNING: openrouter_api_key is empty in Settings object!")
    print("   This might be because Settings was initialized before env vars were loaded.")
PYTHON_SCRIPT
echo ""

# Test 4: Check API Key Status endpoint
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 TEST 4: API Key Status Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s "$API_URL/key/status" | python3 -m json.tool
echo ""

# Test 5: Test OpenRouter API Connection (if key is available)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 TEST 5: OpenRouter API Connection Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -n "$OPENROUTER_KEY" ] && [ "$OPENROUTER_KEY" != "" ]; then
    echo "Testing OpenRouter API connection..."
    docker compose exec -T api python3 << 'PYTHON_SCRIPT'
import asyncio
import httpx
from src.config import settings

async def test_openrouter():
    if not settings.openrouter_api_key:
        print("❌ OPENROUTER_API_KEY not available in settings")
        return
    
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    
    # Simple test request
    payload = {
        "model": "google/gemini-2.0-flash-lite-001",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            if response.status_code == 200:
                print("✅ OpenRouter API connection successful")
            elif response.status_code == 401:
                print("❌ OpenRouter API: Unauthorized (invalid API key)")
            else:
                print(f"⚠️  OpenRouter API: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ OpenRouter API connection failed: {str(e)}")

asyncio.run(test_openrouter())
PYTHON_SCRIPT
else
    echo -e "${YELLOW}⚠️  Skipping: OPENROUTER_API_KEY not set${NC}"
fi
echo ""

# Test 6: Test Speech-to-Text endpoint with MP3 file
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 TEST 6: Speech-to-Text Endpoint Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "test.mp3" ]; then
    echo "Testing transcription with test.mp3..."
    RESULT=$(curl -s -X POST "$API_URL/speech-to-text" \
        -F "audio=@test.mp3")
    
    echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
    
    SUCCESS=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || echo "false")
    if [ "$SUCCESS" = "True" ]; then
        echo -e "${GREEN}✅ Transcription successful!${NC}"
        TEXT=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('text', ''))" 2>/dev/null || echo "")
        if [ -n "$TEXT" ]; then
            echo "   Transcribed text: $TEXT"
        fi
    else
        ERROR=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown error'))" 2>/dev/null || echo "Unknown error")
        echo -e "${RED}❌ Transcription failed: $ERROR${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  test.mp3 file not found${NC}"
    echo "   Create a test audio file or use an existing one"
fi
echo ""

# Test 7: Check .env file
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 TEST 7: .env File Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    if grep -q "^OPENROUTER_API_KEY=" .env; then
        echo -e "${GREEN}✅ OPENROUTER_API_KEY found in .env${NC}"
    else
        echo -e "${RED}❌ OPENROUTER_API_KEY not found in .env${NC}"
    fi
    if grep -q "^KIE_API_KEY=" .env; then
        echo -e "${GREEN}✅ KIE_API_KEY found in .env${NC}"
    else
        echo -e "${RED}❌ KIE_API_KEY not found in .env${NC}"
    fi
else
    echo -e "${RED}❌ .env file does not exist${NC}"
    echo "   Create it from env.example: cp env.example .env"
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "If transcription is still failing, try:"
echo "  1. Restart API container: docker compose restart api"
echo "  2. Recreate container: docker compose up -d --force-recreate api"
echo "  3. Check logs: docker compose logs api | grep -i openrouter"
echo ""

