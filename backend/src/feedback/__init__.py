from __future__ import annotations

from core.models.base import DomainBase
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer

"""Feedback model for feature quality metrics.

- Captures rating/comment across target entities (kind + id) for analytics.
- Index user_id for per-user sentiment analysis.
"""


class Feedback(DomainBase):
    __tablename__ = "feedback"
    __table_args__ = (Index("ix_feedback_user_id", "user_id"),)

    # id / created_at from DomainBase
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    target_kind: Mapped[str] = mapped_column(String(30))
    target_id: Mapped[int] = mapped_column(Integer)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None]
    # created_at from DomainBase
