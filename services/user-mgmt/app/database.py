"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text, event
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async engine with schema configuration
connect_args = {}
if settings.DB_SCHEMA:
    connect_args["server_settings"] = {"search_path": settings.DB_SCHEMA}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args=connect_args
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def init_db():
    """Initialize database (create tables if needed)"""
    async with engine.begin() as conn:
        # Import models to register them
        from app.models import user  # noqa
        # Create tables (for development - use migrations in production)
        # await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """Check if database connection is working"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

