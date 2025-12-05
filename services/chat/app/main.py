"""
Chat Service - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database import init_db
from app.kafka_client import kafka_producer, kafka_consumer
from app.routers import conversations, messages

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info(f"Starting {settings.SERVICE_NAME} service...")
    await init_db()
    
    # Start Kafka producer
    await kafka_producer.start()
    logger.info("Kafka producer started")
    
    # Start Kafka consumer in background
    # await kafka_consumer.start()
    # logger.info("Kafka consumer started")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME} service...")
    await kafka_producer.stop()
    # await kafka_consumer.stop()


app = FastAPI(
    title="Chat Service",
    description="Conversational AI service for Cloud Learning Platform",
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

app.include_router(conversations.router, prefix="/api/chat", tags=["Conversations"])
app.include_router(messages.router, prefix="/api/chat", tags=["Messages"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0"
    }


@app.get("/health/kafka")
async def health_check_kafka():
    """Kafka health check"""
    is_connected = kafka_producer.is_connected()
    return {
        "status": "healthy" if is_connected else "unhealthy",
        "kafka": "connected" if is_connected else "disconnected"
    }

