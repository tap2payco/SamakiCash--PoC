import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Settings:
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # API Keys
    MISTRAL_API_KEY: Optional[str] = os.getenv("MISTRAL_API_KEY")
    ELEVENLABS_API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
    AIML_API_KEY: Optional[str] = os.getenv("AIML_API_KEY")
    NEBIUS_API_KEY: Optional[str] = os.getenv("NEBIUS_API_KEY")
    
    # App Settings
    APP_NAME: str = "SamakiCash API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS Settings
    CORS_ORIGINS: list = [
        "https://samakicash-pwa.onrender.com",
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    
    # Use in-memory database if no DATABASE_URL is provided
    USE_MEMORY_DB: bool = DATABASE_URL is None

settings = Settings()
