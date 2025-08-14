from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer

from src.core.models.base import DomainBase

"""Conversational models mapping to chat feature.

- ConversationSession: chat context (source, locale, plant linkage) with performance metrics potential.
- ChatMessage: stores role, token usage (prompt/completion) for cost tracking & analytics.
- Indexes: user_id (sessions), session_id (messages) for retrieval.
"""


class ConversationSession(DomainBase):
    __tablename__ = "conversation_sessions"
    __table_args__ = (Index("ix_conversation_sessions_user_id", "user_id"),)

    # id / created_at from DomainBase
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    plant_id: Mapped[int | None] = mapped_column(
        ForeignKey("plants.id", ondelete="SET NULL"), nullable=True
    )
    source: Mapped[str | None] = mapped_column(String(30))
    locale: Mapped[str | None] = mapped_column(String(12))
    started_at: Mapped[datetime | None]
    ended_at: Mapped[datetime | None]


class ChatMessage(DomainBase):
    __tablename__ = "chat_messages"

    # id / created_at from DomainBase
    session_id: Mapped[int] = mapped_column(
        ForeignKey("conversation_sessions.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(20))
    content_text: Mapped[str]
    image_url: Mapped[str | None]
    model: Mapped[str | None]
    token_prompt: Mapped[int | None] = mapped_column(Integer)
    token_completion: Mapped[int | None] = mapped_column(Integer)
    # created_at from DomainBase
