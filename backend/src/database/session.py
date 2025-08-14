from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session

from src.core.config import settings

# Example URLs:
# postgresql+psycopg://user:pass@host:5432/dbname
# For local dev, you can use sqlite+aiosqlite or similar, but keep Postgres in prod.

# Sync engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # drops dead connections proactively
    pool_recycle=1800,  # recycle connections (e.g., if behind NAT/proxy)
    pool_size=10,  # tune per deployment
    max_overflow=20,  # extra conns beyond pool_size
    echo=False,  # set True only when debugging SQL
    future=True,  # 2.0-style API
)

# Async engine
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql+psycopg", "postgresql+asyncpg"),
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=10,
    max_overflow=20,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency: yields a SQLAlchemy Session per request.

    Usage:
        def route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # Let services control commits; just ensure consistency on failures.
        db.rollback()
        raise
    finally:
        db.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: yields an async SQLAlchemy Session per request.

    Usage:
        async def route(db: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Optional: if you like a context manager for CLI scripts / jobs
@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Context manager for scripts/workers:
        with session_scope() as db:
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def async_session_scope() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for scripts/workers:
        async with async_session_scope() as db:
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
