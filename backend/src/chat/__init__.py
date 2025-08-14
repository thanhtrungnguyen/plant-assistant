"""Chat module exports"""

# Import routers
try:
    from .routes.chat import router as chat_router
except ImportError:
    chat_router = None

# Import services
try:
    from .services.enhanced_chat_service import EnhancedChatService
except ImportError:
    EnhancedChatService = None

try:
    from .service import ChatService, get_chat_service
except ImportError:
    ChatService = None
    get_chat_service = None

# Import schemas
try:
    from .schemas import ChatRequest, ChatResponse, ChatError, ChatMessage, ChatSession
except ImportError:
    ChatRequest = None
    ChatResponse = None
    ChatError = None
    ChatMessage = None
    ChatSession = None

# Import models
try:
    from .models.chat_models import ChatSession as ChatSessionNew, ChatMessage as ChatMessageNew, ChatKnowledge
except ImportError:
    ChatSessionNew = None
    ChatMessageNew = None
    ChatKnowledge = None

try:
    from .models import (
        ChatSession as ChatSessionModel,
        ChatMessage as ChatMessageModel,
        UserPlantProfile,
        ChatFeedback,
        MessageRole,
    )
except ImportError:
    ChatSessionModel = None
    ChatMessageModel = None
    UserPlantProfile = None
    ChatFeedback = None
    MessageRole = None

__all__ = [
    # Routes
    "chat_router",
    # Services
    "ChatService",
    "get_chat_service",
    "EnhancedChatService",
    # Schemas
    "ChatRequest",
    "ChatResponse",
    "ChatError",
    "ChatMessage",
    "ChatSession",
    # Models
    "ChatSessionModel",
    "ChatMessageModel",
    "ChatSessionNew",
    "ChatMessageNew",
    "ChatKnowledge",
    "UserPlantProfile",
    "ChatFeedback",
    "MessageRole",
]
