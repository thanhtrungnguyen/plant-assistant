from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models.base import DomainBase

"""Reminder models mapping to tracking feature requirements.

- Reminder: stores scheduling & channel metadata for tasks (water, fertilize, etc.).
- ReminderLog: execution results (sent_at, status, error) enabling KPI measurement.
- Indexes: plant_id (reminder), reminder_id (log) for fast dashboard queries.
"""


class Reminder(DomainBase):
    __tablename__ = "reminders"
    __table_args__ = (Index("ix_reminders_plant_id", "plant_id"),)

    # id / created_at from DomainBase
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(500))
    task_type: Mapped[str] = mapped_column(String(30))
    priority: Mapped[str] = mapped_column(String(10), default="medium")
    next_due_date: Mapped[datetime] = mapped_column(nullable=False)
    is_recurring: Mapped[bool] = mapped_column(default=False)
    cron_expression: Mapped[str | None] = mapped_column(String(100))
    is_completed: Mapped[bool] = mapped_column(default=False)
    completed_at: Mapped[datetime | None]
    channel: Mapped[str] = mapped_column(String(30), default="email")
    timezone: Mapped[str | None] = mapped_column(String(64))
    schedule_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    # created_at from DomainBase


class ReminderLog(DomainBase):
    __tablename__ = "reminder_logs"

    # id / created_at from DomainBase
    reminder_id: Mapped[int] = mapped_column(
        ForeignKey("reminders.id", ondelete="CASCADE"), index=True
    )
    sent_at: Mapped[datetime | None]
    status: Mapped[str | None] = mapped_column(String(20))
    error: Mapped[str | None] = mapped_column(String)
