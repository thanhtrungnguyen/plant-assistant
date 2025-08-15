from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer, Numeric

from src.core.models.base import DomainBase
from src.database.base import Base

"""Diagnosis feature models.

Docs mapping:
- Session: tracks model, latency_ms, cost_usd for performance & cost metrics.
- Asset: each uploaded diagnostic image (FK session_id) with CASCADE.
- IssueCatalog: canonical issue definitions (natural key `code`).
- Candidate: ranked potential issues with confidence & remedies markdown.
- Indexes: user_id (sessions), session_id (assets & candidates) for fast retrieval.
"""


class DiagnosisSession(DomainBase):
    __tablename__ = "diagnosis_sessions"
    __table_args__ = (Index("ix_diagnosis_sessions_user_id", "user_id"),)

    # id / created_at from DomainBase
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"))
    description: Mapped[str | None] = mapped_column(String)
    status: Mapped[str | None] = mapped_column(String(30))
    model: Mapped[str | None] = mapped_column(String(100))
    cost_usd: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # created_at from DomainBase


class DiagnosisAsset(DomainBase):
    __tablename__ = "diagnosis_assets"

    # id / created_at from DomainBase
    session_id: Mapped[int] = mapped_column(
        ForeignKey("diagnosis_sessions.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str]


class IssueCatalog(Base):
    __tablename__ = "issue_catalog"
    code: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class DiagnosisCandidate(DomainBase):
    __tablename__ = "diagnosis_candidates"

    # id / created_at from DomainBase
    session_id: Mapped[int] = mapped_column(
        ForeignKey("diagnosis_sessions.id", ondelete="CASCADE"), index=True
    )
    issue_code: Mapped[str | None] = mapped_column(
        ForeignKey("issue_catalog.code", ondelete="SET NULL"), nullable=True
    )
    label_text: Mapped[str]
    confidence: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)
    remedies_markdown: Mapped[str | None]
    expected_timeline_days: Mapped[int | None]
    rank: Mapped[int | None]
