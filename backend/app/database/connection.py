import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger("database_connection")
DATABASE_URL = settings.DATABASE_URL

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,  # Small pool to stay well under Supabase limits
    max_overflow=5,  # No extra connections beyond pool_size
    # Recycle connections every 3 minutes (shorter to avoid idle connections)
    pool_recycle=300,
    pool_timeout=10,  # Wait max 5s for a free connection
    connect_args={"timeout": 20},  # asyncpg connection timeout, ssl will be added for production
)

# Async session class
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Base class for ORM models
Base = declarative_base()


# Test async connection
async def test_async_connection():
    try:
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info(f"Async connection successful! Result: {result.fetchone()}")
    except Exception as e:
        logger.error("Async database connection failed: %s", str(e))
        raise ConnectionError("Failed to connect to the database")


# Helper function to get async session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session