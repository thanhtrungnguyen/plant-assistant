"""Pydantic schemas for chat API."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from .models.chat_message import MessageRole


class ChatMessageBase(BaseModel):
    """Base schema for chat messages."""
    role: MessageRole
    content: str = Field(min_length=1, max_length=10000)


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating chat messages."""
    session_id: Optional[int] = None
    plant_context_ids: Optional[List[int]] = None
    message_metadata: Optional[Dict[str, Any]] = None


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    created_at: datetime
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = None
    message_metadata: Optional[Dict[str, Any]] = None
    retrieved_context: Optional[List[Dict[str, Any]]] = None


class ChatSessionBase(BaseModel):
    """Base schema for chat sessions."""
    title: str = Field(default="New Chat", max_length=200)


class ChatSessionCreate(ChatSessionBase):
    """Schema for creating chat sessions."""
    user_preferences: Optional[Dict[str, Any]] = None
    related_plant_ids: Optional[List[int]] = None


class ChatSessionUpdate(BaseModel):
    """Schema for updating chat sessions."""
    title: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    user_preferences: Optional[Dict[str, Any]] = None
    related_plant_ids: Optional[List[int]] = None


class ChatSessionResponse(ChatSessionBase):
    """Schema for chat session responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    last_activity: datetime
    message_count: int
    context_summary: Optional[str] = None
    related_plant_ids: Optional[List[int]] = None


class ChatSessionWithMessages(ChatSessionResponse):
    """Schema for chat session with messages."""
    messages: List[ChatMessageResponse] = []


class ChatRequest(BaseModel):
    """Schema for chat requests."""
    message: str = Field(min_length=1, max_length=10000, description="User's message")
    session_id: Optional[int] = Field(None, description="Chat session ID (creates new session if None)")
    plant_id: Optional[int] = Field(None, description="Related plant ID for context")
    context: Optional[str] = Field(None, description="Additional context")
    use_rag: bool = Field(True, description="Whether to use RAG for enhanced responses")


class ChatResponse(BaseModel):
    """Schema for chat responses."""
    message: str = Field(description="Assistant's response")
    session_id: int = Field(description="Chat session ID")
    message_id: int = Field(description="Message ID")
    suggestions: List[str] = Field(default_factory=list, description="Follow-up suggestions")
    related_actions: List[str] = Field(default_factory=list, description="Suggested actions")
    confidence: float = Field(ge=0, le=1, description="Response confidence")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    tokens_used: Optional[int] = Field(None, description="Tokens used for generation")
    retrieved_context: Optional[List[Dict[str, Any]]] = Field(None, description="Retrieved context from RAG")


class RAGQueryRequest(BaseModel):
    """Schema for RAG query requests."""
    query: str = Field(min_length=1, max_length=1000)
    namespace: Optional[str] = Field("plant_knowledge", description="Pinecone namespace")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to retrieve")
    score_threshold: float = Field(default=0.7, ge=0, le=1, description="Minimum similarity score")
    include_metadata: bool = Field(True, description="Include metadata in results")


class RAGQueryResponse(BaseModel):
    """Schema for RAG query responses."""
    results: List[Dict[str, Any]] = Field(description="Retrieved documents")
    query_embedding: Optional[List[float]] = Field(None, description="Query embedding vector")
    processing_time: float = Field(description="Query processing time")


class ChatAnalytics(BaseModel):
    """Schema for chat analytics."""
    total_sessions: int
    total_messages: int
    active_sessions: int
    avg_messages_per_session: float
    avg_response_time: float
    common_topics: List[Dict[str, Any]]
    user_satisfaction: Optional[float] = None
