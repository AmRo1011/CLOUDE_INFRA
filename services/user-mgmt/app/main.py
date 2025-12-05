"""
User Management Service - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database import init_db
from app.routers import auth, users

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} service...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME} service...")


# Create FastAPI application
app = FastAPI(
    title="User Management Service",
    description="Authentication, authorization, and user management for Cloud Learning Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0"
    }


@app.get("/health/db")
async def health_check_db():
    """Database health check"""
    from app.database import check_db_connection
    is_connected = await check_db_connection()
    return {
        "status": "healthy" if is_connected else "unhealthy",
        "database": "connected" if is_connected else "disconnected"
    }

