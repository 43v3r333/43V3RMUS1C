"""
Application Configuration
43V3R CORE - Centralized settings management
"""
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="43V3R CORE API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    app_env: str = Field(default="development", description="Environment: development, staging, production")
    app_host: str = Field(default="0.0.0.0", description="Host to bind to")
    app_port: int = Field(default=8000, description="Port to bind to")
    app_debug: bool = Field(default=False, description="Enable debug mode")

    # Security
    secret_key: str = Field(default="changeme-secret-key", description="JWT secret key")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration in days")
    password_min_length: int = Field(default=8, description="Minimum password length")
    algorithm: str = Field(default="HS256", description="JWT algorithm")

    # Database
    database_url: str = Field(
        default="postgresql://versemusic:changeme@localhost:5432/versemusic",
        description="Database connection URL"
    )
    database_pool_size: int = Field(default=20, description="Database pool size")
    database_max_overflow: int = Field(default=10, description="Database max overflow")
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_password: Optional[str] = Field(default=None, description="Redis password")

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/1", description="Celery broker URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", description="Celery result backend")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="CORS allowed origins"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or standard")

    # Storage
    storage_type: str = Field(default="local", description="Storage type: local, s3")
    storage_path: str = Field(default="./storage", description="Local storage path")
    storage_bucket: Optional[str] = Field(default=None, description="S3 bucket name")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret access key")
    aws_region: str = Field(default="us-east-1", description="AWS region")

    # AI Services
    ai_api_key: Optional[str] = Field(default=None, description="AI service API key")
    ai_model: str = Field(default="gpt-4", description="AI model to use")
    ai_max_tokens: int = Field(default=2000, description="AI max tokens")

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.app_env == "production"

    @property
    def database_url_async(self) -> str:
        """Get async database URL"""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()