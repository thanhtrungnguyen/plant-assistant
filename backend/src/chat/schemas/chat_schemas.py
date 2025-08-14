"""Chat schemas for request/response validation."""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class ChatResponse(BaseModel):
    """Chat response schema."""
    session_id: str = Field(..., description="Chat session ID")
    message: str = Field(..., description="AI response message")
    timestamp: datetime = Field(..., description="Response timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Response metadata")


class ChatMessageSchema(BaseModel):
    """Chat message schema."""
    id: str
    session_id: str
    content: str
    role: str
    message_metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionSchema(BaseModel):
    """Chat session schema."""
    id: str
    user_id: int
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageSchema] = []

    class Config:
        from_attributes = True


class ChatHistoryRequest(BaseModel):
    """Chat history request schema."""
    session_id: str = Field(..., description="Chat session ID")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Maximum number of messages")


class ChatHistoryResponse(BaseModel):
    """Chat history response schema."""
    session_id: str
    messages: List[ChatMessageSchema]
    total_count: int


class KnowledgeBaseEntry(BaseModel):
    """Knowledge base entry schema."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    category: Optional[str] = Field(None, max_length=100)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeBaseResponse(BaseModel):
    """Knowledge base response schema."""
    id: str
    title: str
    content: str
    category: Optional[str]
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    """Chat session list response schema."""
    sessions: List[ChatSessionSchema]
    total_count: int


class SearchRequest(BaseModel):
    """Search request schema."""
    query: str = Field(..., min_length=1, max_length=500)
    limit: Optional[int] = Field(5, ge=1, le=20)


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    results: List[str]
    count: int
