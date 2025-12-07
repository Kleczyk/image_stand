"""FastAPI application with LangGraph workflows."""
from typing import Optional
from contextlib import asynccontextmanager
import httpx

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
)
from src.graphs.image_generation import run_image_generation
from src.graphs.image_comparison import run_image_comparison
from src.services.kie_client import encode_image_to_base64
from src.services import image_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("🚀 Image Stand API starting...")
    print(f"📚 API docs: http://{settings.host}:{settings.port}/docs")
    print(f"🔗 LangGraph workflows enabled")
    # Initialize image storage
    image_storage.init_storage()
    print(f"📁 Images directory: {image_storage.IMAGES_DIR}")
    yield
    print("👋 Image Stand API shutting down...")


app = FastAPI(
    title="Image Stand API",
    version="1.0.0",
    description="""
    Image generation and comparison API using kie.ai Nano Banana Pro.
    
    Built with **FastAPI** and **LangGraph** for robust workflow orchestration.
    
    ## Features
    - 🎨 **Text-to-Image**: Generate images from text prompts
    - 🖼️ **Image-to-Image**: Transform images with text guidance
    - 📊 **Image Comparison**: Compare two images for similarity (SSIM)
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
            <li><code>POST /api/compare</code> - Compare two images (SSIM algorithm)</li>
            <li><code>POST /api/key</code> - Set API key</li>
            <li><code>GET /api/key/status</code> - Check API key status</li>
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
):
    """
    Compare two images using LangGraph workflow.
    
    Uses Structural Similarity Index (SSIM) algorithm.
    
    Returns:
    - **similarity_score**: Raw SSIM score (-1 to 1, where 1 is identical)
    - **similarity_percentage**: Normalized to 0-100%
    
    The request flows through a LangGraph state machine:
    1. **Validate**: Check both images are provided
    2. **Compare**: Calculate SSIM similarity
    3. **Output**: Return metrics
    """
    image1_bytes = await image1.read()
    image2_bytes = await image2.read()
    
    # Run LangGraph workflow
    result = await run_image_comparison(
        image1_bytes=image1_bytes,
        image2_bytes=image2_bytes,
    )
    
    return CompareImagesResponse(
        success=result["success"],
        similarity_score=result.get("similarity_score"),
        similarity_percentage=result.get("similarity_percentage"),
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
