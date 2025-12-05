"""
Configuration settings for User Management Service
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Service Info
    SERVICE_NAME: str = "user-mgmt"
    SERVICE_PORT: int = 8001
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/platform_main"
    DB_SCHEMA: str = "user_mgmt"
    
    # JWT Settings
    JWT_SECRET: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # AWS S3
    S3_BUCKET: str = "user-management-storage"
    S3_ENDPOINT_URL: str | None = None  # For LocalStack
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:80"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

