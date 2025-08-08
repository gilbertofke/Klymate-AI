from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Base API Settings
    PROJECT_NAME: str = "Klymate-AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database Settings
    TIDB_HOST: str = "localhost"
    TIDB_PORT: int = 4000
    TIDB_USER: str = ""
    TIDB_PASSWORD: str = ""
    TIDB_DATABASE: str = "klymate_ai"
    
    # Firebase Settings
    FIREBASE_CREDENTIALS_PATH: str = ""
    
    # Environment Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
