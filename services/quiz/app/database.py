"""
Database configuration for Quiz Service
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
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
    connect_args=connect_args
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def init_db():
    logger.info("Database initialized")


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

