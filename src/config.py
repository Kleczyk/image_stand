"""Configuration management for the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
# In Docker, environment variables are set by docker-compose, so this is optional
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API Configuration - stored in memory (for local app without DB)
class Settings:
    """Application settings with runtime-modifiable API key."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Reload environment variables to ensure they're current
            cls._instance._reload_from_env()
        return cls._instance
    
    def _reload_from_env(self):
        """Reload API keys and settings from environment variables."""
        self._kie_api_key = os.getenv("KIE_API_KEY", "")
        self._openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        # Runtime-modifiable sensitivity (can be changed via API)
        self._runtime_sensitivity = None  # None means use env var
    
    @property
    def kie_api_key(self) -> str:
        return self._kie_api_key
    
    @kie_api_key.setter
    def kie_api_key(self, value: str):
        self._kie_api_key = value
    
    @property
    def openrouter_api_key(self) -> str:
        return self._openrouter_api_key
    
    @openrouter_api_key.setter
    def openrouter_api_key(self, value: str):
        self._openrouter_api_key = value
    
    @property
    def django_secret_key(self) -> str:
        return os.getenv("DJANGO_SECRET_KEY", "dev-secret-key-change-me")
    
    @property
    def debug(self) -> bool:
        return os.getenv("DEBUG", "true").lower() == "true"
    
    @property
    def host(self) -> str:
        return os.getenv("HOST", "0.0.0.0")
    
    @property
    def port(self) -> int:
        return int(os.getenv("PORT", "8000"))
    
    @property
    def similarity_model(self) -> str:
        """Similarity model to use: 'ssim', 'embeddings', or 'hybrid'."""
        return os.getenv("SIMILARITY_MODEL", "hybrid").lower()
    
    @property
    def similarity_use_hybrid(self) -> bool:
        """Whether to use hybrid approach (deprecated, use SIMILARITY_MODEL instead)."""
        return os.getenv("SIMILARITY_USE_HYBRID", "true").lower() == "true"
    
    @property
    def similarity_embedding_weight(self) -> float:
        """Weight for embedding similarity in hybrid mode (0.0 to 1.0)."""
        return float(os.getenv("SIMILARITY_EMBEDDING_WEIGHT", "0.7"))
    
    @property
    def similarity_ssim_weight(self) -> float:
        """Weight for SSIM similarity in hybrid mode (0.0 to 1.0)."""
        return float(os.getenv("SIMILARITY_SSIM_WEIGHT", "0.3"))
    
    @property
    def similarity_sensitivity(self) -> float:
        """
        Rigour/strictness adjustment for similarity scores.
        - Higher values (2.0, 3.0, 5.0) = MORE STRICT = LOWER scores
        - Lower values (0.5, 0.7) = MORE LENIENT = HIGHER scores
        - Default 1.0 = no adjustment
        Examples:
        - 2.0: Reduces scores significantly (good for strict comparison)
        - 3.0: Very strict (reduces scores even more)
        - 5.0: Extremely strict (reduces scores dramatically)
        """
        # Use runtime value if set, otherwise use env var
        if self._runtime_sensitivity is not None:
            return self._runtime_sensitivity
        return float(os.getenv("SIMILARITY_SENSITIVITY", "1.0"))
    
    @similarity_sensitivity.setter
    def similarity_sensitivity(self, value: float):
        """Set runtime sensitivity value (overrides env var)."""
        if value < 0.1 or value > 10.0:
            raise ValueError("Sensitivity must be between 0.1 and 10.0")
        self._runtime_sensitivity = value
    
    @property
    def similarity_use_nonlinear(self) -> bool:
        """Whether to use non-linear scaling for better discrimination."""
        return os.getenv("SIMILARITY_USE_NONLINEAR", "true").lower() == "true"
    
    @property
    def similarity_min_threshold(self) -> float:
        """
        Minimum threshold for non-linear scaling.
        Scores below this are considered different images (max 10% similarity).
        Default 0.3.
        """
        return float(os.getenv("SIMILARITY_MIN_THRESHOLD", "0.3"))
    
    @property
    def similarity_max_threshold(self) -> float:
        """
        Maximum threshold for non-linear scaling.
        Scores above this are considered similar images (60%+ similarity).
        Default 0.7.
        """
        return float(os.getenv("SIMILARITY_MAX_THRESHOLD", "0.7"))


settings = Settings()


