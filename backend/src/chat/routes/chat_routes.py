"""Chat API routes for conversational plant assistance."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.auth.dependencies import require_user
from src.auth.models import User
from src.database.session import get_db
from ..schemas import (
    ChatRequest,
    ChatResponse,
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatSessionWithMessages,
    ChatAnalytics
)
from ..services.chat_service import ChatService

# Test schemas
class TestMessageRequest(BaseModel):
    message: str

router = APIRouter(prefix="/chat", tags=["Plant Chat"])

# Add a test endpoint without authentication
@router.get("/test")
async def test_chat_api():
    """Test endpoint to verify chat API is working"""
    return {"status": "ok", "message": "Chat API is working!"}

# Test endpoint for sending a simple message without auth
@router.post("/test-message")
async def test_send_message(
    request: TestMessageRequest,
    db: Session = Depends(get_db)
):
    """Test endpoint for sending a simple message without authentication"""
    try:
        message = request.message
        # Mock response for testing
        response = {
            "message": f"Test response to: {message}",
            "sender": "bot",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


# Real AI chat endpoint without authentication for testing
@router.post("/test-ai-message")
async def test_ai_message(
    request: TestMessageRequest,
    db: Session = Depends(get_db)
):
    """Test AI chat endpoint without authentication"""
    try:
        chat_service = ChatService(db)

        # Create a mock chat request for the AI service
        chat_request = ChatRequest(
            message=request.message,
            use_rag=True,
            plant_id=None,
            image_url=None
        )

        # Get AI response
        ai_response = await chat_service.process_chat_message(chat_request, user_id=1)  # Mock user ID

        return {
            "status": "success",
            "response": {
                "message": ai_response.message,
                "sender": "bot",
                "timestamp": ai_response.timestamp.isoformat(),
                "confidence": ai_response.confidence_score,
                "suggestions": ai_response.suggestions,
                "retrieved_context": ai_response.retrieved_context
            }
        }
    except Exception as e:
        # Fallback to simple response if AI fails
        fallback_response = {
            "message": f"Xin lỗi, tôi hiện đang gặp sự cố kỹ thuật với AI. Về câu hỏi '{request.message}', bạn có thể tham khảo các nguồn tài liệu chăm sóc cây trồng hoặc thử lại sau.",
            "sender": "bot",
            "timestamp": "2024-01-01T00:00:00Z",
            "confidence": 0.1
        }
        return {"status": "fallback", "response": fallback_response, "error": str(e)}


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    """Get chat service instance."""
    return ChatService(db)


@router.post("/", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(require_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Chat with the plant care assistant.

    This endpoint processes user messages and returns AI-generated responses
    enhanced with relevant plant care knowledge through RAG (Retrieval-Augmented Generation).
    """
    try:
        response = await chat_service.process_chat_message(request, current_user.id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process chat message")


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(require_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Create a new chat session."""
    try:
        return await chat_service.create_chat_session(session_data, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create chat session")


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_user_chat_sessions(
    active_only: bool = Query(True, description="Return only active sessions"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of sessions to return"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    current_user: User = Depends(require_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Get user's chat sessions."""
    try:
        return await chat_service.get_user_sessions(
            user_id=current_user.id,
            active_only=active_only,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve chat sessions")


@router.get("/sessions/{session_id}", response_model=ChatSessionWithMessages)
async def get_chat_session_with_messages(
    session_id: int,
    message_limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of messages returned"),
    current_user: User = Depends(require_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Get a chat session with its messages."""
    try:
        session = await chat_service.get_session_with_messages(
            session_id=session_id,
            user_id=current_user.id,
            message_limit=message_limit
        )

        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")

        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve chat session")


@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: int,
    session_update: ChatSessionUpdate,
    current_user: User = Depends(require_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Update a chat session."""
    try:
        session = await chat_service.update_session(
            session_id=session_id,
            user_id=current_user.id,
            title=session_update.title,
            is_active=session_update.is_active,
            user_preferences=session_update.user_preferences,
            related_plant_ids=session_update.related_plant_ids
        )

        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")

        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update chat session")


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(require_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Delete a chat session and all its messages."""
    try:
        success = await chat_service.delete_session(session_id, current_user.id)

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete chat session")


@router.get("/analytics", response_model=ChatAnalytics)
async def get_chat_analytics(
    current_user: User = Depends(require_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Get chat analytics for the current user."""
    try:
        stats = await chat_service.get_chat_analytics(current_user.id)

        return ChatAnalytics(
            total_sessions=stats["total_sessions"],
            total_messages=stats["total_messages"],
            active_sessions=stats["active_sessions"],
            avg_messages_per_session=stats["avg_messages_per_session"],
            avg_response_time=stats["avg_response_time"],
            common_topics=[],  # TODO: Implement topic analysis
            user_satisfaction=None  # TODO: Implement satisfaction tracking
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve chat analytics")


# Health check for chat service
@router.get("/health")
async def chat_service_health():
    """Health check for chat service."""
    return {
        "status": "healthy",
        "service": "chat",
        "features": [
            "conversational_ai",
            "rag_enhanced_responses",
            "session_management",
            "plant_context_awareness"
        ]
    }
