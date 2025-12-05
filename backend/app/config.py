from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from typing import List


load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "Research Assistant for PDFs"
    API_VERSION: str = "1.0.0"
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Environment
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # PDF Configuration
    MAX_PDF_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["application/pdf"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

