"""FastAPI application with LangGraph workflows."""
from typing import Optional
from contextlib import asynccontextmanager
import httpx
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.schemas import (
    GenerateImageResponse,
    CompareImagesResponse,
    ApiKeyRequest,
    ApiKeyResponse,
    HealthResponse,
    SpeechToTextResponse,
    SensitivityRequest,
    SensitivityResponse,
)
from src.graphs.image_generation import run_image_generation
from src.graphs.image_comparison import run_image_comparison, set_executor
from src.services.kie_client import encode_image_to_base64
from src.services import image_storage
from src.services.openrouter_client import transcribe_audio
from src.services.image_embeddings import get_embedder


# Thread pool executor for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="image-compare")

# Set executor for image comparison graph
set_executor(executor)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("🚀 Image Stand API starting...")
    print(f"📚 API docs: http://{settings.host}:{settings.port}/docs")
    print(f"🔗 LangGraph workflows enabled")
    # Initialize image storage
    image_storage.init_storage()
    print(f"📁 Images directory: {image_storage.IMAGES_DIR}")
    
    # Pre-load CLIP model in background to avoid first-request timeout
    print("🔄 Pre-loading CLIP model for image embeddings...")
    try:
        # Load model in thread pool to avoid blocking startup
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, _preload_clip_model)
        print("✅ CLIP model pre-loaded successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not pre-load CLIP model: {e}")
        print("   Image comparison will use SSIM fallback or load on first use")
    
    yield
    print("👋 Image Stand API shutting down...")
    executor.shutdown(wait=True)


def _preload_clip_model():
    """Pre-load CLIP model synchronously."""
    try:
        embedder = get_embedder()
        if embedder:
            # Try to extract a dummy embedding to ensure model is fully loaded
            from PIL import Image
            import numpy as np
            from io import BytesIO
            # Create a tiny test image
            test_img = Image.new('RGB', (224, 224), color='white')
            img_bytes = BytesIO()
            test_img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            _ = embedder.extract_embedding(img_bytes.getvalue())
            print("   CLIP model is ready")
    except Exception as e:
        print(f"   CLIP model pre-load failed: {e}")


app = FastAPI(
    title="Image Stand API",
    version="1.0.0",
    description="""
    Image generation and comparison API using kie.ai Nano Banana Pro.
    
    Built with **FastAPI** and **LangGraph** for robust workflow orchestration.
    
    ## Features
    - 🎨 **Text-to-Image**: Generate images from text prompts
    - 🖼️ **Image-to-Image**: Transform images with text guidance
    - 📊 **Image Comparison**: Compare two images for similarity (SSIM, embeddings, hybrid)
    - 🎯 **Similarity Rigour Control**: Adjustable strictness for image comparison (0.1-10.0)
    - 🎤 **Speech-to-Text**: Convert audio to text using Google Gemini 2.0 Flash Lite via OpenRouter
    - 🔑 **API Key Management**: Runtime API key configuration
    - 🔄 **LangGraph Workflows**: Stateful graph-based processing
    """,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Home Page =====

@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with API information."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Stand API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #eee;
                min-height: 100vh;
            }
            h1 { color: #a855f7; }
            h2 { color: #818cf8; margin-top: 2rem; }
            a { color: #60a5fa; }
            code {
                background: #2d2d44;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.9em;
            }
            ul { line-height: 2; }
            .badge {
                display: inline-block;
                background: #7c3aed;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                margin-left: 8px;
            }
        </style>
    </head>
    <body>
        <h1>🖼️ Image Stand API</h1>
        <p>Image generation and comparison API using kie.ai Nano Banana Pro.</p>
        <p><span class="badge">FastAPI</span> <span class="badge">LangGraph</span></p>
        
        <h2>📚 Documentation</h2>
        <ul>
            <li><a href="/docs">Swagger UI (Interactive)</a></li>
            <li><a href="/redoc">ReDoc (Clean)</a></li>
        </ul>
        
        <h2>🔗 Endpoints</h2>
        <ul>
            <li><code>POST /api/generate</code> - Generate image from text (+ optional input image)</li>
            <li><code>POST /api/compare</code> - Compare two images (SSIM, embeddings, or hybrid)</li>
            <li><code>POST /api/speech-to-text</code> - Convert audio to text (WebM, WAV, MP3)</li>
            <li><code>POST /api/key</code> - Set API key</li>
            <li><code>GET /api/key/status</code> - Check API key status</li>
            <li><code>POST /api/sensitivity</code> - Set similarity rigour/strictness (0.1-10.0)</li>
            <li><code>GET /api/sensitivity</code> - Get current similarity rigour value</li>
            <li><code>GET /api/health</code> - Health check</li>
        </ul>
        
        <h2>🔄 LangGraph Workflows</h2>
        <p>This API uses LangGraph for stateful workflow orchestration:</p>
        <ul>
            <li><strong>Image Generation Graph</strong>: validate → generate → output</li>
            <li><strong>Image Comparison Graph</strong>: validate → compare → output</li>
        </ul>
    </body>
    </html>
    """


# ===== API Endpoints =====

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check API health and configuration status."""
    return HealthResponse(
        status="ok",
        api_key_configured=bool(settings.kie_api_key),
        langgraph_enabled=True,
    )


@app.post("/api/generate", response_model=GenerateImageResponse)
async def generate_image(
    prompt: str = Form(..., description="Text description of the image to generate"),
    aspect_ratio: str = Form("1:1", description="Aspect ratio: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, auto"),
    resolution: str = Form("1K", description="Resolution: 1K, 2K, 4K"),
    output_format: str = Form("png", description="Output format: png, jpg"),
    image_url: Optional[str] = Form(None, description="URL of image to edit (for img2img)"),
):
    """
    Generate or edit an image using LangGraph workflow.
    
    - **Text-to-Image**: Provide only a prompt (uses nano-banana-pro)
    - **Image-to-Image**: Provide prompt + image_url for editing (uses nano-banana-edit)
    
    The request flows through a LangGraph state machine:
    1. **Validate**: Check inputs and API key
    2. **Generate**: Call kie.ai API
    3. **Output**: Return result with image URL
    
    Images are automatically downloaded and stored locally.
    Access via /images/{filename} endpoint.
    """
    # Run LangGraph workflow
    result = await run_image_generation(
        prompt=prompt,
        image_url=image_url,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        output_format=output_format,
    )
    
    local_url = None
    
    # Download and save image locally if generation succeeded
    if result["success"] and result.get("image_url"):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                img_response = await client.get(result["image_url"])
                if img_response.status_code == 200:
                    # Generate filename from task_id
                    task_id = result.get("task_id", "unknown")
                    ext = output_format
                    filename = image_storage.generate_filename(task_id, ext)
                    
                    # Save locally
                    image_storage.save_image(filename, img_response.content)
                    local_url = f"/images/{filename}"
        except Exception as e:
            # Image download failed, but generation succeeded
            pass
    
    return GenerateImageResponse(
        success=result["success"],
        image_url=result.get("image_url"),
        image_urls=result.get("image_urls"),
        local_url=local_url,
        task_id=result.get("task_id"),
        state=result.get("state"),
        error=result.get("error"),
    )


@app.post("/api/compare", response_model=CompareImagesResponse)
async def compare_images(
    image1: UploadFile = File(..., description="First image to compare"),
    image2: UploadFile = File(..., description="Second image to compare"),
    method: Optional[str] = Form(None, description="Comparison method: 'ssim', 'embeddings', or 'hybrid' (default from config)"),
    sensitivity: Optional[float] = Form(None, description="Rigour/strictness: Higher values (2.0-5.0) = more strict/lower scores, lower values (0.5-0.8) = more lenient/higher scores, default 1.0"),
):
    """
    Compare two images using LangGraph workflow.
    
    Supports multiple comparison algorithms:
    - **ssim**: Structural Similarity Index (pixel-based)
    - **embeddings**: CLIP embeddings with cosine similarity (semantic)
    - **hybrid**: Combines embeddings (70%) + SSIM (30%) - recommended for AI images
    
    Returns:
    - **similarity_score**: Raw similarity score (-1 to 1, where 1 is identical)
    - **similarity_percentage**: Normalized to 0-100%
    - **method**: Which comparison method was used
    
    The request flows through a LangGraph state machine:
    1. **Validate**: Check both images are provided
    2. **Compare**: Calculate similarity using selected method
    3. **Output**: Return metrics
    """
    try:
        image1_bytes = await image1.read()
        image2_bytes = await image2.read()
    except Exception as e:
        return CompareImagesResponse(
            success=False,
            error=f"Failed to read image files: {str(e)}"
        )
    
    # Validate method parameter
    if method and method not in ["ssim", "embeddings", "hybrid"]:
        raise HTTPException(
            status_code=400,
            detail="Method must be one of: 'ssim', 'embeddings', or 'hybrid'"
        )
    
    # Run LangGraph workflow with timeout
    try:
        result = await asyncio.wait_for(
            run_image_comparison(
                image1_bytes=image1_bytes,
                image2_bytes=image2_bytes,
                method=method,
                sensitivity=sensitivity,
            ),
            timeout=60.0  # 60 second timeout for comparison
        )
    except asyncio.TimeoutError:
        # If timeout, fallback to SSIM (faster)
        print("⚠️  Comparison timeout, falling back to SSIM")
        from src.services.comparison import compare_images as compare_ssim
        loop = asyncio.get_event_loop()
        result_obj = await loop.run_in_executor(
            executor,
            compare_ssim,
            image1_bytes,
            image2_bytes
        )
        result = {
            "success": result_obj.success,
            "similarity_score": result_obj.similarity_score,
            "similarity_percentage": result_obj.similarity_percentage,
            "method_used": "ssim",
            "error": result_obj.error,
        }
    except Exception as e:
        return CompareImagesResponse(
            success=False,
            error=f"Comparison failed: {str(e)}"
        )
    
    return CompareImagesResponse(
        success=result["success"],
        similarity_score=result.get("similarity_score"),
        similarity_percentage=result.get("similarity_percentage"),
        method=result.get("method_used"),
        error=result.get("error"),
    )


@app.post("/api/key", response_model=ApiKeyResponse)
async def update_api_key(data: ApiKeyRequest):
    """
    Update the kie.ai API key.
    
    The key is stored in memory and will be reset when the server restarts.
    For persistence, set the KIE_API_KEY environment variable.
    """
    if not data.api_key or len(data.api_key) < 10:
        return ApiKeyResponse(
            success=False,
            message="Invalid API key format (must be at least 10 characters)"
        )
    
    settings.kie_api_key = data.api_key
    return ApiKeyResponse(
        success=True,
        message="API key updated successfully"
    )


@app.get("/api/key/status", response_model=ApiKeyResponse)
async def get_api_key_status():
    """Check if API key is configured."""
    if settings.kie_api_key:
        masked = settings.kie_api_key[:4] + "..." + settings.kie_api_key[-4:]
        return ApiKeyResponse(
            success=True,
            message=f"API key configured: {masked}"
        )
    return ApiKeyResponse(
        success=False,
        message="API key not configured"
    )


@app.post("/api/sensitivity", response_model=SensitivityResponse)
async def update_sensitivity(data: SensitivityRequest):
    """
    Update the similarity sensitivity/rigour parameter.
    
    The sensitivity controls how strict the image comparison is:
    - Higher values (2.0, 3.0, 5.0) = MORE STRICT = LOWER similarity scores
    - Lower values (0.5, 0.7) = MORE LENIENT = HIGHER similarity scores
    - Default 1.0 = no adjustment
    
    Examples:
    - 2.0: Reduces scores significantly (good for strict comparison)
    - 3.0: Very strict (reduces scores even more)
    - 5.0: Extremely strict (reduces scores dramatically)
    
    The value is stored in memory and will be reset when the server restarts.
    For persistence, set the SIMILARITY_SENSITIVITY environment variable.
    """
    try:
        if data.sensitivity < 0.1 or data.sensitivity > 10.0:
            return SensitivityResponse(
                success=False,
                message=f"Invalid sensitivity value: {data.sensitivity}. Must be between 0.1 and 10.0",
                sensitivity=settings.similarity_sensitivity
            )
        
        settings.similarity_sensitivity = data.sensitivity
        return SensitivityResponse(
            success=True,
            message=f"Sensitivity updated to {data.sensitivity}",
            sensitivity=data.sensitivity
        )
    except ValueError as e:
        return SensitivityResponse(
            success=False,
            message=str(e),
            sensitivity=settings.similarity_sensitivity
        )


@app.get("/api/sensitivity", response_model=SensitivityResponse)
async def get_sensitivity():
    """Get the current similarity sensitivity/rigour value."""
    current_sensitivity = settings.similarity_sensitivity
    return SensitivityResponse(
        success=True,
        message=f"Current sensitivity: {current_sensitivity}",
        sensitivity=current_sensitivity
    )


@app.post("/api/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(
    audio: UploadFile = File(..., description="Audio file to transcribe (WebM, WAV, MP3, etc.)"),
):
    """
    Convert speech to text using Google Gemini 2.0 Flash Lite via OpenRouter.ai.
    
    Accepts audio files in various formats (WebM, WAV, MP3, OGG) and returns
    the transcribed text ready to use as a prompt for image generation.
    
    **Supported formats:**
    - WebM (typical for browser recordings)
    - WAV
    - MP3
    - OGG
    
    **Returns:**
    - **success**: Whether transcription succeeded
    - **text**: Transcribed text (if successful)
    - **error**: Error message (if failed)
    
    **Example usage:**
    1. Record audio from microphone in browser (WebM format)
    2. Send POST request with audio file
    3. Receive transcribed text
    4. Use text as prompt for image generation
    """
    # Validate file
    if not audio.filename:
        return SpeechToTextResponse(
            success=False,
            error="No audio file provided"
        )
    
    # Read audio bytes
    try:
        audio_bytes = await audio.read()
        if not audio_bytes or len(audio_bytes) == 0:
            return SpeechToTextResponse(
                success=False,
                error="Audio file is empty"
            )
    except Exception as e:
        return SpeechToTextResponse(
            success=False,
            error=f"Failed to read audio file: {str(e)}"
        )
    
    # Determine MIME type from content type or filename
    mime_type = audio.content_type
    if not mime_type or not mime_type.startswith("audio/"):
        # Try to infer from filename
        filename_lower = audio.filename.lower()
        if filename_lower.endswith(".webm"):
            mime_type = "audio/webm"
        elif filename_lower.endswith(".wav"):
            mime_type = "audio/wav"
        elif filename_lower.endswith(".mp3"):
            mime_type = "audio/mpeg"
        elif filename_lower.endswith(".ogg"):
            mime_type = "audio/ogg"
        else:
            # Default to webm (most common for browser recordings)
            mime_type = "audio/webm"
    
    # Validate MIME type
    valid_mime_types = [
        "audio/webm",
        "audio/wav",
        "audio/wave",
        "audio/mpeg",
        "audio/mp3",
        "audio/ogg",
        "audio/opus",
    ]
    if mime_type not in valid_mime_types:
        return SpeechToTextResponse(
            success=False,
            error=f"Unsupported audio format: {mime_type}. Supported formats: {', '.join(valid_mime_types)}"
        )
    
    # Transcribe audio
    try:
        transcribed_text = await transcribe_audio(audio_bytes, mime_type)
        return SpeechToTextResponse(
            success=True,
            text=transcribed_text,
        )
    except ValueError as e:
        # API key not configured
        return SpeechToTextResponse(
            success=False,
            error=str(e),
        )
    except httpx.HTTPError as e:
        # API request failed
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            error_msg = "Invalid or missing OpenRouter API key. Set OPENROUTER_API_KEY environment variable."
        elif "429" in error_msg:
            error_msg = "Rate limit exceeded. Please try again later."
        return SpeechToTextResponse(
            success=False,
            error=f"Transcription failed: {error_msg}",
        )
    except Exception as e:
        return SpeechToTextResponse(
            success=False,
            error=f"Unexpected error: {str(e)}",
        )


# ===== Image Serving =====

@app.get("/images/{filename}")
async def get_image(filename: str):
    """
    Serve a locally stored image.
    
    Images are automatically saved when generated via /api/generate.
    """
    filepath = image_storage.get_image_path(filename)
    if filepath is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Determine media type
    media_type = "image/png"
    if filename.endswith(".jpg") or filename.endswith(".jpeg"):
        media_type = "image/jpeg"
    
    return FileResponse(filepath, media_type=media_type)


@app.get("/api/images", response_model=dict)
async def list_images():
    """List all locally stored images."""
    images = image_storage.list_images()
    return {
        "count": len(images),
        "images": [f"/images/{img}" for img in images],
    }


# ===== Run with uvicorn =====

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
