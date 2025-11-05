"""
Database configuration and session management.
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Base class for models
Base = declarative_base()

# Initialize database components only if not in demo mode
engine: Optional[any] = None
AsyncSessionLocal: Optional[any] = None

if not settings.DEMO_MODE and settings.DATABASE_URL:
    # Convert postgresql:// to postgresql+asyncpg://
    DATABASE_URL = str(settings.DATABASE_URL).replace(
        "postgresql://", "postgresql+asyncpg://"
    )

    # Create async engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DB_ECHO_LOG,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        future=True,
    )

    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    In demo mode, this returns None and should not be used.

    Yields:
        AsyncSession: Database session
    """
    if settings.DEMO_MODE:
        # In demo mode, yield a mock session that won't be used
        yield None
        return

    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Set DATABASE_URL or enable DEMO_MODE.")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    if settings.DEMO_MODE or engine is None:
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connection."""
    if settings.DEMO_MODE or engine is None:
        return
    await engine.dispose()
