"""
Document Service - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database import init_db
from app.kafka_client import kafka_producer
from app.routers import documents, notes

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.SERVICE_NAME} service...")
    await init_db()
    await kafka_producer.start()
    yield
    logger.info(f"Shutting down {settings.SERVICE_NAME} service...")
    await kafka_producer.stop()


app = FastAPI(
    title="Document Service",
    description="Document upload and processing for Cloud Learning Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(notes.router, prefix="/api/documents", tags=["Notes"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0"
    }


@app.get("/health/kafka")
async def health_check_kafka():
    return {
        "status": "healthy" if kafka_producer.is_connected() else "unhealthy",
        "kafka": "connected" if kafka_producer.is_connected() else "disconnected"
    }

