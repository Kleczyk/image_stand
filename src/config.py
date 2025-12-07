"""Configuration management for the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
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
            cls._instance._kie_api_key = os.getenv("KIE_API_KEY", "")
        return cls._instance
    
    @property
    def kie_api_key(self) -> str:
        return self._kie_api_key
    
    @kie_api_key.setter
    def kie_api_key(self, value: str):
        self._kie_api_key = value
    
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


