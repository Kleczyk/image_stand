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
        """Reload API keys from environment variables."""
        self._kie_api_key = os.getenv("KIE_API_KEY", "")
        self._openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
    
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


settings = Settings()


