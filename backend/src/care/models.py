from __future__ import annotations

from datetime import date

from src.core.models.base import DomainBase, UpdatedAtMixin
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer

"""Care advice models.

Docs mapping:
- CarePlan: versioned generated plan with inputs_json capturing personalization context.
- CareTaskTemplate: structured recurring tasks derived from plan (watering, fertilizing etc.).
- Index plant_id for fast retrieval of latest plan when generating updates.
"""


class CarePlan(UpdatedAtMixin, DomainBase):
    __tablename__ = "care_plans"
    __table_args__ = (Index("ix_care_plans_plant_id", "plant_id"),)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer)
    generated_by: Mapped[str | None] = mapped_column(String(100))
    inputs_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    plan_markdown: Mapped[str] = mapped_column(String)
    valid_from: Mapped[date | None]
    valid_to: Mapped[date | None]
    # created_at / updated_at from mixins


class CareTaskTemplate(DomainBase):
    __tablename__ = "care_task_templates"
    care_plan_id: Mapped[int] = mapped_column(
        ForeignKey("care_plans.id", ondelete="CASCADE"), index=True
    )
    task_type: Mapped[str] = mapped_column(String(30))
    cadence_days: Mapped[int | None]
    cron: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(String)
