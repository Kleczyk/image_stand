"""Image embedding extraction using pre-trained CNN models."""
import torch
import torch.nn.functional as F
from io import BytesIO
from typing import Optional
import numpy as np
from PIL import Image

try:
    from transformers import CLIPProcessor, CLIPModel
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

from src.config import settings


class ImageEmbedder:
    """Extract feature vectors from images using pre-trained CLIP model."""
    
    _instance = None
    _model = None
    _processor = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the embedder (lazy loading)."""
        if self._model is None and CLIP_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        """Load CLIP model and processor (lazy loading)."""
        if not CLIP_AVAILABLE:
            raise ImportError(
                "CLIP model not available. Install with: pip install transformers torch"
            )
        
        try:
            # Use ViT-B/32 for balance of speed and accuracy
            model_name = "openai/clip-vit-base-patch32"
            print(f"Loading CLIP model: {model_name}...")
            self._processor = CLIPProcessor.from_pretrained(model_name)
            self._model = CLIPModel.from_pretrained(model_name)
            self._model.eval()  # Set to evaluation mode
            
            # Move to CPU (can be changed to GPU if available)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model = self._model.to(device)
            self._device = device
            print(f"CLIP model loaded on {device}")
        except Exception as e:
            raise RuntimeError(f"Failed to load CLIP model: {str(e)}")
    
    def extract_embedding(self, image_bytes: bytes) -> np.ndarray:
        """
        Extract embedding vector from image.
        
        Args:
            image_bytes: Image file as bytes
            
        Returns:
            Normalized embedding vector as numpy array
        """
        if not CLIP_AVAILABLE:
            raise ImportError("CLIP model not available")
        
        if self._model is None:
            self._load_model()
        
        try:
            # Load and preprocess image
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # Process image with CLIP processor
            inputs = self._processor(images=image, return_tensors="pt")
            
            # Move inputs to same device as model
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Extract features (no gradient computation for inference)
            with torch.no_grad():
                image_features = self._model.get_image_features(**inputs)
                
                # Normalize features (L2 normalization)
                image_features = F.normalize(image_features, p=2, dim=1)
            
            # Convert to numpy and flatten
            embedding = image_features.cpu().numpy().flatten()
            
            return embedding
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract embedding: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if CLIP model is available."""
        return CLIP_AVAILABLE and self._model is not None


# Global instance (singleton)
_embedder: Optional[ImageEmbedder] = None


def get_embedder() -> Optional[ImageEmbedder]:
    """Get or create the global embedder instance."""
    global _embedder
    if _embedder is None and CLIP_AVAILABLE:
        try:
            _embedder = ImageEmbedder()
        except Exception as e:
            print(f"Warning: Could not initialize CLIP embedder: {e}")
            return None
    return _embedder


def extract_image_embedding(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Extract embedding from image bytes.
    
    Args:
        image_bytes: Image file as bytes
        
    Returns:
        Embedding vector or None if model not available
    """
    embedder = get_embedder()
    if embedder is None:
        return None
    
    try:
        return embedder.extract_embedding(image_bytes)
    except Exception as e:
        print(f"Error extracting embedding: {e}")
        return None


