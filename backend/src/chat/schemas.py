"""
Chat API Request/Response Schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Individual chat message schema"""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default=None, description="Message timestamp")


class ChatRequest(BaseModel):
    """Chat request with message and optional image"""

    message: str = Field(
        ..., description="User message content", min_length=1, max_length=2000
    )
    image_base64: Optional[str] = Field(
        default=None, description="Base64 encoded image for plant analysis"
    )
    session_id: Optional[str] = Field(
        default=None, description="Chat session ID for conversation continuity"
    )
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=[], description="Previous messages in conversation"
    )


class ChatResponse(BaseModel):
    """Chat response with assistant message and metadata"""

    message: str = Field(..., description="Assistant response message")
    session_id: str = Field(..., description="Chat session ID")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Response timestamp"
    )
    suggestions: Optional[List[str]] = Field(
        default=[], description="Suggested follow-up questions"
    )
    plant_identified: Optional[bool] = Field(
        default=None, description="Whether a plant was identified in the image"
    )
    confidence_score: Optional[float] = Field(
        default=None, description="Confidence score for plant identification (0-1)"
    )


class ChatError(BaseModel):
    """Chat error response schema"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    session_id: Optional[str] = Field(
        default=None, description="Session ID if available"
    )


class ChatSession(BaseModel):
    """Chat session metadata"""

    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Session creation time"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Last update time"
    )
    message_count: int = Field(default=0, description="Number of messages in session")
    metadata: Optional[Dict[str, Any]] = Field(
        default={}, description="Additional session metadata"
    )
