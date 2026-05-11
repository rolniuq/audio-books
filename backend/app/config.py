import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AudioBook API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    DATABASE_URL: str = "sqlite:///./data/audiobook.db"
    
    STORAGE_DIR: str = "app/storage"
    BOOKS_DIR: str = "app/storage/books"
    
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024
    
    DEFAULT_VOICE: str = "vi-VN-HoaiMyNeural"
    DEFAULT_LANGUAGE: str = "vi-VN"
    
    TTS_SEGMENT_SIZE: int = 5000
    CHAPTER_FALLBACK_WORDS: int = 3000

    MAX_RETRIES: int = 3
    RETRY_BASE_DELAY: float = 1.0
    RETRY_MAX_DELAY: float = 60.0

settings = Settings()