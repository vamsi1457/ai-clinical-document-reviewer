import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Explicitly load .env from backend directory and repository root
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")
load_dotenv(".env")


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Clinical Document Reviewer"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/clinical_db"
    
    # AI Configuration
    AI_API_KEY: str = ""
    AI_MODEL: str = "gemini-2.0-flash"
    AI_PROVIDER: str = "auto"  # 'auto', 'gemini', 'openai'
    AI_BASE_URL: str = ""
    
    # CORS & Frontend
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:80",
        "http://localhost",
    ]
    
    # File Limits & Storage
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "png", "jpg", "jpeg"]
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg",
    ]
    
    # OCR Settings
    TESSERACT_CMD: str = ""
    OCR_ENGINE: str = "auto"  # 'auto', 'tesseract', 'rapidocr'
    
    model_config = SettingsConfigDict(
        env_file=(
            str(BACKEND_DIR / ".env"),
            str(ROOT_DIR / ".env"),
            ".env"
        ),
        extra="ignore"
    )


settings = Settings()
