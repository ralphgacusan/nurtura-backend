"""
core/database.py

This module sets up the SQLAlchemy Async Database Engine and Session for use with FastAPI.

Features:
- Asynchronous engine creation using SQLAlchemy's AsyncIO support
- Declarative Base for ORM models
- Session factory (SessionLocal) for creating async sessions
- FastAPI dependency (`get_session`) for injecting database sessions into routes
"""

# -------------------------
# Imports
# -------------------------
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession  # Async DB engine and session
from sqlalchemy.orm import sessionmaker, declarative_base            # ORM session and base class for models
from app.core.config import settings                                  # Application settings for DB connection

# -------------------------
# Async Database Engine
# -------------------------
engine = create_async_engine(
    settings.DATABASE_URL,  # Database connection URL from config
    echo=True               # Echo SQL queries for debugging/logging purposes
)

# -------------------------
# Async Session Factory
# -------------------------
SessionLocal = sessionmaker(
    bind=engine,            # Bind session factory to the async engine
    expire_on_commit=False, # Do not expire objects after commit (keep them accessible)
    class_=AsyncSession     # Use AsyncSession for async support
)

# -------------------------
# Declarative Base for ORM models
# -------------------------
Base = declarative_base()  # Base class for defining ORM models

# -------------------------
# FastAPI Dependency
# -------------------------
async def get_session():
    """
    FastAPI dependency that provides a SQLAlchemy async session to route handlers.

    Usage in routes:
        @router.get("/items/")
        async def read_items(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Item))
            items = result.scalars().all()
            return items

    Yields:
        AsyncSession: A SQLAlchemy async session
    """
    async with SessionLocal() as session:
        yield session