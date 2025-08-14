from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models.base import DomainBase, UpdatedAtMixin
from src.database.base import Base

"""Plant domain models.

Business requirements mapping:
- Tracking & Reminders (tracking feature doc):
    * Dashboard performance (<1s for ~50 plants) -> index on user_id.
    * Photo history, notes, location -> PlantPhoto + Plant optional text fields.
    * Sharing/permissions -> PlantShare composite PK (plant_id,user_id, role).
- Care Advice: species_id FK enables personalized care plan generation.

Design notes:
- PlantShare uses composite PK (no surrogate id) + created_at for minimal audit.
- Relationships/back_populates deferred; can be added when service layer implemented.
- Potential future compound index (user_id, is_archived) if archived filtering is frequent.

Non-functional alignment:
- Security & deletion: CASCADE ensures user data removal request propagates.
- Performance: JSONB (ai_metrics_json) optional to minimize storage when unused.
"""


class Plant(UpdatedAtMixin, DomainBase):
    __tablename__ = "plants"
    __table_args__ = (
        Index("ix_plants_user_id", "user_id"),
        # Basic validation for geospatial-lite coordinates
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_plants_lat_range"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_plants_lon_range"),
    )

    # id / created_at from DomainBase, updated_at from UpdatedAtMixin
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    species_id: Mapped[int | None] = mapped_column(
        ForeignKey("species.id", ondelete="SET NULL"), nullable=True
    )
    nickname: Mapped[str | None] = mapped_column(String)
    location_text: Mapped[str | None] = mapped_column(String)
    # Geospatial-lite (upgrade to PostGIS Point for advanced queries later)
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]
    acquisition_date: Mapped[datetime | None]
    light_conditions: Mapped[str | None] = mapped_column(String)
    soil_type: Mapped[str | None] = mapped_column(String)
    notes: Mapped[str | None] = mapped_column(String)
    is_archived: Mapped[bool] = mapped_column(default=False)
    ai_metrics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # timestamps provided by mixins


class PlantShare(Base):
    __tablename__ = "plant_shares"
    plant_id: Mapped[int] = mapped_column(
        ForeignKey("plants.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PlantPhoto(DomainBase):
    __tablename__ = "plant_photos"

    # id / created_at from DomainBase
    plant_id: Mapped[int] = mapped_column(
        ForeignKey("plants.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(String)
    taken_at: Mapped[datetime | None]
    caption: Mapped[str | None] = mapped_column(String)
    ai_metrics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # created_at from DomainBase
