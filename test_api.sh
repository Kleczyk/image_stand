#!/bin/bash

# Image Stand API - Automatic Test Script
# ========================================

API_URL="http://localhost:8000/api"
API_KEY="beccec7dac1774165b23de2412bcd70c"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          IMAGE STAND API - AUTOMATIC TEST                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 TEST 1: Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s "$API_URL/health" | python3 -m json.tool
echo ""

# 2. Set API Key
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 TEST 2: Set API Key"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s -X POST "$API_URL/key" \
    -H "Content-Type: application/json" \
    -d "{\"api_key\": \"$API_KEY\"}" | python3 -m json.tool
echo ""

# 3. Check API Key Status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 TEST 3: API Key Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s "$API_URL/key/status" | python3 -m json.tool
echo ""

# 4. Generate Image (Text-to-Image)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 TEST 4: Generate Image (text-to-image)"
echo "   Prompt: 'A cute cartoon cat with blue eyes'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏳ Generating... (wait ~30s)"

RESULT1=$(curl -s -X POST "$API_URL/generate" \
    -F "prompt=A cute cartoon dog with blue eyes" \
    -F "resolution=1K" \
    -F "aspect_ratio=1:1")

echo "$RESULT1" | python3 -m json.tool

# Extract URLs
IMAGE_URL=$(echo "$RESULT1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('image_url',''))" 2>/dev/null)
LOCAL_URL=$(echo "$RESULT1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('local_url',''))" 2>/dev/null)
echo ""

# 5. Check local image via endpoint
if [ -n "$LOCAL_URL" ] && [ "$LOCAL_URL" != "null" ] && [ "$LOCAL_URL" != "None" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📁 TEST 5: Access Local Image"
    echo "   URL: http://localhost:8000$LOCAL_URL"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000$LOCAL_URL")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Image accessible (HTTP $HTTP_CODE)"
        # Save a copy
        curl -s -o "Test_local_copy.png" "http://localhost:8000$LOCAL_URL"
        echo "✅ Saved copy as: Test_local_copy.png"
    else
        echo "❌ Image not accessible (HTTP $HTTP_CODE)"
    fi
    echo ""
fi

# 6. List stored images
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📂 TEST 6: List Stored Images"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s "$API_URL/images" | python3 -m json.tool
echo ""

# 7. Edit Image (Image-to-Image) - only if we got URL
if [ -n "$IMAGE_URL" ] && [ "$IMAGE_URL" != "null" ] && [ "$IMAGE_URL" != "None" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🖌️  TEST 7: Edit Image (image-to-image)"
    echo "   Input: $IMAGE_URL"
    echo "   Prompt: 'Add sunglasses and a party hat'"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⏳ Editing... (wait ~30s)"
    
    RESULT2=$(curl -s -X POST "$API_URL/generate" \
        -F "prompt=Add sunglasses and a party hat" \
        -F "image_url=$IMAGE_URL")
    
    echo "$RESULT2" | python3 -m json.tool
    
    EDITED_LOCAL=$(echo "$RESULT2" | python3 -c "import sys,json; print(json.load(sys.stdin).get('local_url',''))" 2>/dev/null)
    echo ""
    
    # 8. Compare Images (if both exist locally)
    if [ -n "$EDITED_LOCAL" ] && [ "$EDITED_LOCAL" != "null" ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📊 TEST 8: Compare Images (SSIM)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Download both images for comparison
        curl -s -o "/tmp/img1.png" "http://localhost:8000$LOCAL_URL"
        curl -s -o "/tmp/img2.png" "http://localhost:8000$EDITED_LOCAL"
        
        curl -s -X POST "$API_URL/compare" \
            -F "image1=@/tmp/img1.png" \
            -F "image2=@/tmp/img2.png" | python3 -m json.tool
        echo ""
    fi
else
    echo "⚠️  TEST 7: SKIPPED (no image URL from generation)"
    echo "⚠️  TEST 8: SKIPPED (no images to compare)"
    echo ""
fi

# 9. Final list of images
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📂 TEST 9: Final List of Stored Images"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s "$API_URL/images" | python3 -m json.tool
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    TEST COMPLETE                           ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Images stored in: ./images/                               ║"
echo "║  Access via: http://localhost:8000/images/{filename}       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🔗 URLs:"
[ -n "$LOCAL_URL" ] && [ "$LOCAL_URL" != "null" ] && echo "   Original: http://localhost:8000$LOCAL_URL"
[ -n "$EDITED_LOCAL" ] && [ "$EDITED_LOCAL" != "null" ] && echo "   Edited:   http://localhost:8000$EDITED_LOCAL"
echo ""
echo "📁 Local files in ./images/:"
ls -la ./images/ 2>/dev/null || echo "   (directory will be created on first run)"
