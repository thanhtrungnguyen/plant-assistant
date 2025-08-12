# src/database/base.py
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from sqlalchemy import MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, Integer

# Alembic-friendly naming conventions
NAMING_CONVENTION = {
    "ix": "ix__%(table_name)s__%(column_0_N_name)s",
    "uq": "uq__%(table_name)s__%(column_0_N_name)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(column_0_N_name)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Common column aliases
int_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
utc_now = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Postgres NOW() AT TIME ZONE 'UTC' if DB is in UTC
        nullable=False,
    ),
]


class TimestampMixin:
    created_at: Mapped[datetime] = utc_now  # type: ignore
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
