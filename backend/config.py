"""
Configuration management for Klymate AI Backend

This module handles loading and validation of environment variables
and application configuration settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///test.db", env="DATABASE_URL")
    tidb_host: str = Field(default="localhost", env="TIDB_HOST")
    tidb_port: int = Field(default=4000, env="TIDB_PORT")
    tidb_user: str = Field(default="test_user", env="TIDB_USER")
    tidb_password: str = Field(default="test_password", env="TIDB_PASSWORD")
    tidb_database: str = Field(default="test_db", env="TIDB_DATABASE")
    
    # Firebase Configuration
    firebase_project_id: str = Field(default="test-project", env="FIREBASE_PROJECT_ID")
    firebase_private_key_id: str = Field(default="test-key-id", env="FIREBASE_PRIVATE_KEY_ID")
    firebase_private_key: str = Field(default="-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----", env="FIREBASE_PRIVATE_KEY")
    firebase_client_email: str = Field(default="test@test-project.iam.gserviceaccount.com", env="FIREBASE_CLIENT_EMAIL")
    firebase_client_id: str = Field(default="test-client-id", env="FIREBASE_CLIENT_ID")
    firebase_auth_uri: str = Field(default="https://accounts.google.com/o/oauth2/auth", env="FIREBASE_AUTH_URI")
    firebase_token_uri: str = Field(default="https://oauth2.googleapis.com/token", env="FIREBASE_TOKEN_URI")
    
    # JWT Configuration
    jwt_secret_key: str = Field(default="test-secret-key-for-development-only", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="test-openai-key", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-ada-002", env="OPENAI_EMBEDDING_MODEL")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # CORS Configuration
    allowed_origins: str = Field(default="*", env="ALLOWED_ORIGINS")
    allowed_methods: str = Field(default="*", env="ALLOWED_METHODS")
    allowed_headers: str = Field(default="*", env="ALLOWED_HEADERS")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()