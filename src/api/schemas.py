"""Pydantic schemas for API requests and responses."""
from typing import Optional, Literal
from pydantic import BaseModel


class GenerateImageResponse(BaseModel):
    """Response schema for image generation."""
    success: bool
    image_url: Optional[str] = None
    image_urls: Optional[list] = None
    local_url: Optional[str] = None
    task_id: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None


class CompareImagesResponse(BaseModel):
    """Response schema for image comparison."""
    success: bool
    similarity_score: Optional[float] = None
    similarity_percentage: Optional[float] = None
    method: Optional[str] = None  # "ssim", "embeddings", or "hybrid"
    error: Optional[str] = None


class ApiKeyRequest(BaseModel):
    """Request schema for API key update."""
    api_key: str


class ApiKeyResponse(BaseModel):
    """Response schema for API key operations."""
    success: bool
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    api_key_configured: bool
    langgraph_enabled: bool = True


class SpeechToTextResponse(BaseModel):
    """Response schema for speech-to-text transcription."""
    success: bool
    text: Optional[str] = None
    error: Optional[str] = None


class SensitivityRequest(BaseModel):
    """Request schema for sensitivity/rigour update."""
    sensitivity: float


class SensitivityResponse(BaseModel):
    """Response schema for sensitivity operations."""
    success: bool
    message: str
    sensitivity: Optional[float] = None
