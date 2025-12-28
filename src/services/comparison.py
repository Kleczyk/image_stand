"""Image comparison service using structural similarity and deep learning embeddings."""
from io import BytesIO
from dataclasses import dataclass
from typing import Optional

import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from src.services.image_embeddings import extract_image_embedding
from src.config import settings


@dataclass
class ComparisonResult:
    """Result of image comparison."""
    success: bool
    similarity_score: Optional[float] = None  # Raw SSIM score (-1 to 1) or embedding similarity (-1 to 1)
    similarity_percentage: Optional[float] = None  # Normalized to 0-100%
    method: Optional[str] = None  # "ssim", "embeddings", or "hybrid"
    error: Optional[str] = None


def apply_nonlinear_scaling(
    raw_score: float,
    sensitivity: float = 1.0,
    min_threshold: float = 0.3,
    max_threshold: float = 0.7,
    use_nonlinear: bool = True,
) -> float:
    """
    Apply non-linear scaling to better separate dissimilar vs similar images.
    
    Strategy:
    - Scores below min_threshold → compress aggressively (max 10%)
    - Scores above max_threshold → expand to allow 60%+
    - Scores in between → gradual transition
    
    Args:
        raw_score: Raw similarity score (typically -1 to 1, but CLIP is 0 to 1)
        sensitivity: Sensitivity adjustment (higher = more strict)
        min_threshold: Below this = different images (default 0.3)
        max_threshold: Above this = similar images (default 0.7)
        use_nonlinear: Whether to apply non-linear scaling (default True)
    
    Returns:
        Scaled score in range -1 to 1 (for percentage conversion)
    """
    if not use_nonlinear:
        return raw_score
    
    # Adjust thresholds based on sensitivity
    # Higher sensitivity → lower thresholds (more strict)
    # Lower sensitivity → higher thresholds (more lenient)
    adjusted_min = min_threshold / sensitivity
    adjusted_max = max_threshold * sensitivity
    
    # Ensure thresholds are in valid range
    adjusted_min = max(0.0, min(0.5, adjusted_min))
    adjusted_max = max(0.5, min(1.0, adjusted_max))
    
    # Normalize raw_score to 0-1 range if it's in -1 to 1 range
    # CLIP embeddings are already 0-1, SSIM is -1 to 1
    if raw_score < 0:
        # SSIM score in -1 to 0 range, normalize to 0-0.5
        normalized_score = (raw_score + 1) / 2
    else:
        # Already in 0-1 range or positive SSIM
        normalized_score = max(0.0, min(1.0, raw_score))
    
    # Apply piecewise linear scaling
    if normalized_score < adjusted_min:
        # Low scores: compress to 0-10% range
        # Map [0, adjusted_min] to [0, 0.1]
        scaled = normalized_score * (0.1 / adjusted_min) if adjusted_min > 0 else 0.0
    elif normalized_score > adjusted_max:
        # High scores: expand to 60-100% range
        # Map [adjusted_max, 1.0] to [0.6, 1.0]
        range_size = 1.0 - adjusted_max
        if range_size > 0:
            scaled = 0.6 + (normalized_score - adjusted_max) * (0.4 / range_size)
        else:
            scaled = 0.6
    else:
        # Middle scores: linear interpolation between 10% and 60%
        # Map [adjusted_min, adjusted_max] to [0.1, 0.6]
        middle_range = adjusted_max - adjusted_min
        if middle_range > 0:
            scaled = 0.1 + (normalized_score - adjusted_min) * (0.5 / middle_range)
        else:
            scaled = 0.1
    
    # Convert back to -1 to 1 range for consistency with existing code
    # scaled is in 0-1, convert to -1 to 1
    return (scaled * 2) - 1


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
            method="ssim",
        )
        
    except Exception as e:
        return ComparisonResult(
            success=False,
            error=f"Image comparison failed: {str(e)}"
        )


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score (-1 to 1)
    """
    # Normalize vectors
    vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
    vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)
    
    # Calculate cosine similarity
    similarity = np.dot(vec1_norm, vec2_norm)
    
    return float(similarity)


def compare_images_embeddings(
    image1_bytes: bytes,
    image2_bytes: bytes,
    sensitivity: float = 1.0,
) -> ComparisonResult:
    """
    Compare two images using CLIP embeddings and cosine similarity.
    
    Args:
        image1_bytes: First image as bytes
        image2_bytes: Second image as bytes
        sensitivity: Sensitivity adjustment (default 1.0)
    
    Returns:
        ComparisonResult with similarity metrics
    """
    try:
        # Extract embeddings
        emb1 = extract_image_embedding(image1_bytes)
        emb2 = extract_image_embedding(image2_bytes)
        
        if emb1 is None or emb2 is None:
            # Fallback to SSIM if embeddings not available
            return compare_images(image1_bytes, image2_bytes)
        
        # Calculate cosine similarity
        # CLIP embeddings are normalized, so cosine similarity ranges from 0 to 1 (not -1 to 1)
        similarity = cosine_similarity(emb1, emb2)
        
        # CLIP cosine similarity is typically 0.0-1.0 for normalized embeddings
        # Clamp to ensure it's in valid range
        similarity = max(0.0, min(1.0, similarity))
        
        # Apply non-linear scaling if enabled
        use_nonlinear = settings.similarity_use_nonlinear
        min_threshold = settings.similarity_min_threshold
        max_threshold = settings.similarity_max_threshold
        
        if use_nonlinear:
            # Apply scaling (expects 0-1 range, returns -1 to 1)
            scaled_similarity = apply_nonlinear_scaling(
                similarity,
                sensitivity=sensitivity,
                min_threshold=min_threshold,
                max_threshold=max_threshold,
                use_nonlinear=True,
            )
        else:
            # Convert 0-1 to -1 to 1 for consistency
            scaled_similarity = (similarity * 2) - 1
        
        # Normalize to percentage (scaled_similarity is now in -1 to 1 range)
        percentage = (scaled_similarity + 1) / 2 * 100
        
        # Ensure percentage is in valid range
        percentage = max(0.0, min(100.0, percentage))
        
        return ComparisonResult(
            success=True,
            similarity_score=round(similarity, 4),  # Store original 0-1 score
            similarity_percentage=round(percentage, 2),
            method="embeddings",
        )
        
    except Exception as e:
        return ComparisonResult(
            success=False,
            error=f"Embedding comparison failed: {str(e)}"
        )


def compare_images_hybrid(
    image1_bytes: bytes,
    image2_bytes: bytes,
    embedding_weight: float = 0.7,
    ssim_weight: float = 0.3,
    sensitivity: float = 1.0,
) -> ComparisonResult:
    """
    Compare two images using hybrid approach: CLIP embeddings + SSIM.
    
    Args:
        image1_bytes: First image as bytes
        image2_bytes: Second image as bytes
        embedding_weight: Weight for embedding similarity (default 0.7)
        ssim_weight: Weight for SSIM similarity (default 0.3)
        sensitivity: Sensitivity adjustment (lower = higher scores, default 1.0)
    
    Returns:
        ComparisonResult with similarity metrics
    """
    try:
        # Normalize weights
        total_weight = embedding_weight + ssim_weight
        if total_weight > 0:
            embedding_weight = embedding_weight / total_weight
            ssim_weight = ssim_weight / total_weight
        else:
            embedding_weight = 0.7
            ssim_weight = 0.3
        
        # Get SSIM score
        ssim_result = compare_images(image1_bytes, image2_bytes)
        if not ssim_result.success:
            # If SSIM fails, try embeddings only
            return compare_images_embeddings(image1_bytes, image2_bytes, sensitivity)
        
        # Get embedding similarity (don't apply non-linear scaling here, we'll do it after combining)
        # Get raw embedding score (0-1 range for CLIP)
        emb1 = extract_image_embedding(image1_bytes)
        emb2 = extract_image_embedding(image2_bytes)
        
        if emb1 is None or emb2 is None:
            # If embeddings fail, use SSIM only
            ssim_result.method = "ssim"
            return ssim_result
        
        # Calculate raw embedding similarity (0-1 range)
        emb_similarity = cosine_similarity(emb1, emb2)
        emb_similarity = max(0.0, min(1.0, emb_similarity))
        
        # Convert SSIM score (-1 to 1) to 0-1 range for combination
        # SSIM score is already in -1 to 1 range
        ssim_score_normalized = (ssim_result.similarity_score + 1) / 2  # Convert to 0-1
        
        # Weighted combination (both scores now in 0-1 range)
        combined_score = (ssim_score_normalized * ssim_weight) + (emb_similarity * embedding_weight)
        
        # Ensure combined score is in 0-1 range
        combined_score = max(0.0, min(1.0, combined_score))
        
        # Apply non-linear scaling if enabled
        use_nonlinear = settings.similarity_use_nonlinear
        min_threshold = settings.similarity_min_threshold
        max_threshold = settings.similarity_max_threshold
        
        if use_nonlinear:
            # Apply non-linear scaling (expects 0-1 range, returns -1 to 1)
            scaled_score = apply_nonlinear_scaling(
                combined_score,
                sensitivity=sensitivity,
                min_threshold=min_threshold,
                max_threshold=max_threshold,
                use_nonlinear=True,
            )
        else:
            # Apply old sensitivity adjustment for backward compatibility
            if sensitivity != 1.0 and combined_score > 0:
                if sensitivity >= 2.0:
                    adjusted_score = combined_score / sensitivity
                else:
                    adjusted_score = combined_score ** (1.0 / sensitivity)
            else:
                adjusted_score = combined_score
            
            # Convert to -1 to 1 range
            scaled_score = (adjusted_score * 2) - 1
        
        # Normalize to percentage (scaled_score is now in -1 to 1 range)
        percentage = (scaled_score + 1) / 2 * 100
        
        # Ensure percentage is in valid range
        percentage = max(0.0, min(100.0, percentage))
        
        return ComparisonResult(
            success=True,
            similarity_score=round(combined_score, 4),
            similarity_percentage=round(percentage, 2),
            method="hybrid",
        )
        
    except Exception as e:
        return ComparisonResult(
            success=False,
            error=f"Hybrid comparison failed: {str(e)}"
        )


