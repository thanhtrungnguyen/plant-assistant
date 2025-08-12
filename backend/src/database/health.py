from __future__ import annotations

from sqlalchemy import text

from src.core.logging import get_logger
from src.database.session import engine

logger = get_logger(__name__)


def db_ready() -> bool:
    """Return True if a simple SELECT works against the DB engine."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.debug("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
