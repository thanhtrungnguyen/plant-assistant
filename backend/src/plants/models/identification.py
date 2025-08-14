from __future__ import annotations

from core.models.base import DomainBase
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer, Numeric

"""Identification feature models.

Docs mapping:
- Photos (1-5) per session -> IdentificationAsset rows.
- Track latency_ms & cost_usd for performance/cost metrics.
- Alternative candidates with confidence & rationale -> IdentificationCandidate.
- species_id optional linkage; label_text for free-form AI label.
- EXIF + dimensions stored for future quality heuristics.

Indexes: user_id (session), session_id (asset/candidate) support fast retrieval.
"""


class IdentificationSession(DomainBase):
    __tablename__ = "identification_sessions"
    __table_args__ = (Index("ix_identification_sessions_user_id", "user_id"),)

    # id / created_at from DomainBase
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    plant_id: Mapped[int | None] = mapped_column(
        ForeignKey("plants.id", ondelete="SET NULL"), nullable=True
    )
    prompt_text: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String(20))
    model: Mapped[str | None] = mapped_column(String(100))
    cost_usd: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # created_at from DomainBase


class IdentificationAsset(DomainBase):
    __tablename__ = "identification_assets"

    # id / created_at from DomainBase
    session_id: Mapped[int] = mapped_column(
        ForeignKey("identification_sessions.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(String)
    width: Mapped[int | None]
    height: Mapped[int | None]
    exif_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class IdentificationCandidate(DomainBase):
    __tablename__ = "identification_candidates"

    # id / created_at from DomainBase
    session_id: Mapped[int] = mapped_column(
        ForeignKey("identification_sessions.id", ondelete="CASCADE"), index=True
    )
    species_id: Mapped[int | None] = mapped_column(
        ForeignKey("species.id", ondelete="SET NULL"), nullable=True
    )
    label_text: Mapped[str] = mapped_column(String)
    confidence: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    rationale_text: Mapped[str | None] = mapped_column(String)
    rank: Mapped[int | None]
