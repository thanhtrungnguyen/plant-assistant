from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class DomainBase(Base):
    """Abstract base with integer primary key and created_at."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class UpdatedAtMixin:
    """Mixin providing updated_at column."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


__all__ = ["DomainBase", "UpdatedAtMixin"]
