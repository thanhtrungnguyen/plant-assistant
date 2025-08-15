from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.core.config import settings

# Example URLs:
# postgresql+psycopg://user:pass@host:5432/dbname (for psycopg 3 - sync mode)
# postgresql+psycopg2://user:pass@host:5432/dbname (for psycopg2 - if using legacy driver)
# For local dev, you can use sqlite but keep Postgres in prod.

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # drops dead connections proactively
    pool_recycle=1800,  # recycle connections (e.g., if behind NAT/proxy)
    pool_size=10,  # tune per deployment
    max_overflow=20,  # extra conns beyond pool_size
    echo=False,  # set True only when debugging SQL
    future=True,  # 2.0-style API
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
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
