"""
Application configuration management
"""
import os
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "43v3r-core"
    app_version: str = "1.0.0"
    app_env: str = "development"
    
    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_debug: bool = True
    
    # Database
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "versemusic"
    postgres_user: str = "versemusic"
    postgres_password: str = "changeme"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = ""
    
    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
        return f"redis://{self.redis_host}:{self.redis_port}/0"
    
    # Celery
    @property
    def celery_broker_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/1"
    
    @property
    def celery_result_backend(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/2"
    
    # JWT Authentication
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:13000"]
    
    # File Storage
    storage_type: str = "local"
    storage_path: str = "/app/storage"
    media_path: str = "/app/storage/media"
    assets_path: str = "/app/storage/assets"
    temp_path: str = "/app/storage/temp"
    
    # FFmpeg
    ffmpeg_path: str = "/usr/bin/ffmpeg"
    ffmpeg_timeout: int = 3600
    
    # External Services
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    
    # Analytics
    analytics_enabled: bool = True
    analytics_retention_days: int = 90
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()