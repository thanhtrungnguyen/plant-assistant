"""Conversational chat schemas for plant assistance."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Schema for a chat message."""

    role: str = Field(description="Role: 'user' or 'assistant'")
    content: str = Field(description="Message content")
    timestamp: Optional[str] = None


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
