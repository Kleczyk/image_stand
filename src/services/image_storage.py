"""Local image storage service."""
from pathlib import Path
from typing import Optional
import os

# Directory for storing images
IMAGES_DIR = Path(os.getenv("IMAGES_DIR", "/app/images"))


def init_storage():
    """Initialize storage directory."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def save_image(filename: str, data: bytes) -> Path:
    """
    Save image data to local storage.
    
    Args:
        filename: Name of the file (e.g., "abc123.png")
        data: Image bytes
    
    Returns:
        Full path to saved file
    """
    init_storage()
    filepath = IMAGES_DIR / filename
    filepath.write_bytes(data)
    return filepath


def get_image_path(filename: str) -> Optional[Path]:
    """
    Get full path to an image file.
    
    Args:
        filename: Name of the file
    
    Returns:
        Path if file exists, None otherwise
    """
    filepath = IMAGES_DIR / filename
    if filepath.exists():
        return filepath
    return None


def list_images() -> list[str]:
    """List all stored images."""
    init_storage()
    return [f.name for f in IMAGES_DIR.iterdir() if f.is_file()]


def delete_image(filename: str) -> bool:
    """
    Delete an image file.
    
    Args:
        filename: Name of the file
    
    Returns:
        True if deleted, False if not found
    """
    filepath = IMAGES_DIR / filename
    if filepath.exists():
        filepath.unlink()
        return True
    return False


def generate_filename(task_id: str, extension: str = "png") -> str:
    """
    Generate a unique filename based on task ID.
    
    Args:
        task_id: Task ID from kie.ai
        extension: File extension
    
    Returns:
        Filename string
    """
    return f"{task_id}.{extension}"


