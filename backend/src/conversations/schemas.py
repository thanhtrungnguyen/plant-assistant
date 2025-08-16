"""Conversational chat schemas for plant assistance."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Schema for a chat message."""

    role: str = Field(description="Role: 'user' or 'assistant'")
    content: str = Field(description="Message content")
    timestamp: Optional[str] = None


class ChatHistoryMessage(BaseModel):
    """Schema for chat history message."""

    id: int
    role: str = Field(description="Role: 'user' or 'assistant'")
    content_text: str = Field(description="Message content")
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSessionResponse(BaseModel):
    """Schema for conversation session with messages."""

    id: int
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    messages: List[ChatHistoryMessage] = []

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Schema for chat history response."""

    sessions: List[ConversationSessionResponse] = []
    total_sessions: int = 0


class ChatRequest(BaseModel):
    """Schema for chat request."""

    message: str = Field(max_length=1000, description="User's message")
    context: Optional[str] = Field(None, description="Additional context")
    plant_id: Optional[int] = Field(None, description="Related plant ID if applicable")


class ChatResponse(BaseModel):
    """Schema for chat response."""

    message: str = Field(description="Assistant's response")
    suggestions: List[str] = Field(
        default_factory=list, description="Follow-up suggestions"
    )
    related_actions: List[str] = Field(
        default_factory=list, description="Suggested actions"
    )
    confidence: float = Field(ge=0, le=1, description="Response confidence")
