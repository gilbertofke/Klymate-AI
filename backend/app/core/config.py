"""
Unified Configuration for Klymate AI Backend

This module combines the comprehensive configuration from both implementations
to provide a single source of truth for all application settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

class Settings(BaseSettings):
    """Unified application settings combining both implementations."""
    
    # API Settings
    PROJECT_NAME: str = "Klymate-AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite:///test.db", env="DATABASE_URL")
    TIDB_HOST: str = Field(default="localhost", env="TIDB_HOST")
    TIDB_PORT: int = Field(default=4000, env="TIDB_PORT")
    TIDB_USER: str = Field(default="test_user", env="TIDB_USER")
    TIDB_PASSWORD: str = Field(default="test_password", env="TIDB_PASSWORD")
    TIDB_DATABASE: str = Field(default="klymate_ai", env="TIDB_DATABASE")
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: str = Field(default="test-project", env="FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY_ID: str = Field(default="test-key-id", env="FIREBASE_PRIVATE_KEY_ID")
    FIREBASE_PRIVATE_KEY: str = Field(default="-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----", env="FIREBASE_PRIVATE_KEY")
    FIREBASE_CLIENT_EMAIL: str = Field(default="test@test-project.iam.gserviceaccount.com", env="FIREBASE_CLIENT_EMAIL")
    FIREBASE_CLIENT_ID: str = Field(default="test-client-id", env="FIREBASE_CLIENT_ID")
    FIREBASE_AUTH_URI: str = Field(default="https://accounts.google.com/o/oauth2/auth", env="FIREBASE_AUTH_URI")
    FIREBASE_TOKEN_URI: str = Field(default="https://oauth2.googleapis.com/token", env="FIREBASE_TOKEN_URI")
    
    # JWT Configuration
    SECRET_KEY: str = Field(default="test-secret-key-for-development-only", env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(default="test-secret-key-for-development-only", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Redis Configuration for Caching (Task 9.2)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_SSL: bool = Field(default=False, env="REDIS_SSL")
    
    # Cache Configuration
    CACHE_DEFAULT_EXPIRE: int = Field(default=300, env="CACHE_DEFAULT_EXPIRE")  # 5 minutes
    CACHE_ANALYTICS_EXPIRE: int = Field(default=1800, env="CACHE_ANALYTICS_EXPIRE")  # 30 minutes
    CACHE_USER_DATA_EXPIRE: int = Field(default=600, env="CACHE_USER_DATA_EXPIRE")  # 10 minutes
    CACHE_LEADERBOARD_EXPIRE: int = Field(default=900, env="CACHE_LEADERBOARD_EXPIRE")  # 15 minutes
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(default="test-openai-key", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-ada-002", env="OPENAI_EMBEDDING_MODEL")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(default="*", env="ALLOWED_ORIGINS")
    ALLOWED_METHODS: str = Field(default="*", env="ALLOWED_METHODS")
    ALLOWED_HEADERS: str = Field(default="*", env="ALLOWED_HEADERS")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )
    # Cache Configuration (Task 9.2)
    CACHE_ENABLED: bool = Field(default=True, env="CACHE_ENABLED")
    CACHE_DEFAULT_TTL: int = Field(default=3600, env="CACHE_DEFAULT_TTL")  # 1 hour
    CACHE_KEY_PREFIX: str = Field(default="klymate:", env="CACHE_KEY_PREFIX")
    REDIS_MAX_CONNECTIONS: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    
    # Analytics Cache TTL Settings
    DASHBOARD_CACHE_TTL: int = Field(default=1800, env="DASHBOARD_CACHE_TTL")  # 30 minutes
    TRENDS_CACHE_TTL: int = Field(default=3600, env="TRENDS_CACHE_TTL")  # 1 hour
    LEADERBOARD_CACHE_TTL: int = Field(default=900, env="LEADERBOARD_CACHE_TTL")  # 15 minutes
    PLATFORM_STATS_CACHE_TTL: int = Field(default=7200, env="PLATFORM_STATS_CACHE_TTL")  # 2 hours

# Global settings instance
settings = Settings()