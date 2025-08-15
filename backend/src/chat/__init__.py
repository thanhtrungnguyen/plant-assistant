"""Chat module for conversational plant assistance.

This module provides AI-powered chat functionality with:
- Natural language conversation about plant care
- RAG (Retrieval-Augmented Generation) enhanced responses
- Session management and conversation history
- Integration with plant identification and care features
- Vector database storage for plant knowledge
"""

from .models import ChatSession, ChatMessage
from .schemas import ChatRequest, ChatResponse, ChatSessionResponse
from .services import ChatService, RAGService, LangChainChatService
from .routes import chat_router, rag_router

__all__ = [
    # Models
    "ChatSession",
    "ChatMessage",

    # Schemas
    "ChatRequest",
    "ChatResponse",
    "ChatSessionResponse",

    # Services
    "ChatService",
    "RAGService",
    "LangChainChatService",

    # Routes
    "chat_router",
    "rag_router",
]
