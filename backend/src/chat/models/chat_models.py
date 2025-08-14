"""Chat models for database storage."""
from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from src.database.base import Base, TimestampMixin


class ChatSession(Base, TimestampMixin):
    """Chat session model."""
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False)  # Reference to user
    title = Column(String(255), nullable=True)

    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Chat message model."""
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    message_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")


class ChatKnowledge(Base, TimestampMixin):
    """Knowledge base entries for chat."""
    __tablename__ = "chat_knowledge"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, default=list)
    knowledge_metadata = Column(JSON, default=dict)
    vector_id = Column(String, nullable=True)  # Reference to Pinecone vector
