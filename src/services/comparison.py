"""Image comparison service using structural similarity."""
from io import BytesIO
from dataclasses import dataclass
from typing import Optional

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim


@dataclass
class ComparisonResult:
    """Result of image comparison."""
    success: bool
    similarity_score: Optional[float] = None  # Raw SSIM score (-1 to 1)
    similarity_percentage: Optional[float] = None  # Normalized to 0-100%
    error: Optional[str] = None


def compare_images(image1_bytes: bytes, image2_bytes: bytes) -> ComparisonResult:
    """
    Compare two images using Structural Similarity Index (SSIM).
    
    Args:
        image1_bytes: First image as bytes
        image2_bytes: Second image as bytes
    
    Returns:
        ComparisonResult with similarity metrics
    """
    try:
        # Load images
        img1 = Image.open(BytesIO(image1_bytes))
        img2 = Image.open(BytesIO(image2_bytes))
        
        # Convert to RGB if needed
        if img1.mode != "RGB":
            img1 = img1.convert("RGB")
        if img2.mode != "RGB":
            img2 = img2.convert("RGB")
        
        # Resize to same dimensions (use smaller image's dimensions)
        target_size = (
            min(img1.width, img2.width),
            min(img1.height, img2.height)
        )
        img1 = img1.resize(target_size, Image.Resampling.LANCZOS)
        img2 = img2.resize(target_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy arrays
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        # Calculate SSIM (channel_axis=2 for RGB images)
        # win_size must be odd and <= image dimensions
        min_dim = min(target_size)
        win_size = min(7, min_dim if min_dim % 2 == 1 else min_dim - 1)
        
        score = ssim(arr1, arr2, channel_axis=2, win_size=win_size)
        
        # Normalize score to percentage (SSIM ranges from -1 to 1)
        percentage = (score + 1) / 2 * 100
        
        return ComparisonResult(
            success=True,
            similarity_score=round(score, 4),
            similarity_percentage=round(percentage, 2),
        )
        
    except Exception as e:
        return ComparisonResult(
            success=False,
            error=f"Image comparison failed: {str(e)}"
        )


