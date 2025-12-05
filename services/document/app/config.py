"""
Configuration settings for Document Service
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    SERVICE_NAME: str = "document"
    SERVICE_PORT: int = 8002
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/platform_main"
    DB_SCHEMA: str = "document"
    
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    S3_BUCKET: str = "document-service-storage"
    S3_ENDPOINT_URL: str | None = None
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    
    JWT_SECRET: str = "your-super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    
    USER_MGMT_URL: str = "http://localhost:8001"
    
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: str = "pdf,docx,txt,md"
    
    OPENAI_API_KEY: str = ""
    
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:80"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()

