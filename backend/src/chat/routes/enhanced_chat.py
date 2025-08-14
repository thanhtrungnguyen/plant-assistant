"""
Enhanced Chat API Routes - with Personalization
Provides conversational interface for plant care assistance with personalized responses.
"""

from typing import Union, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from ..schemas import ChatRequest, ChatResponse, ChatError

router = APIRouter(prefix="/chat", tags=["Plant Care Chat"])
security = HTTPBearer()


@router.post(
    "/",
    response_model=Union[ChatResponse, ChatError],
    summary="Chat with Plant Care Assistant",
    description="""
    Send a message to the plant care AI assistant with personalization. Features include:

    **🤖 Personalized Responses**: Tailored advice based on your experience and plant history
    **🔍 Image Analysis**: Upload plant images for AI-powered health diagnosis
    **📚 Context Memory**: Maintains conversation history and learns your preferences
    **🌱 Plant Knowledge**: Comprehensive plant care guidance with Pinecone-powered context
    **💬 Session Management**: Persistent chat sessions across multiple conversations

    **Usage Examples:**
    - Text only: "Cây của tôi bị vàng lá, nguyên nhân gì?"
    - With image: Upload image + "Cây này có bệnh gì không?"
    - Follow-up: Continue conversation with session_id for context

    **Image Requirements:**
    - Base64 encoded string
    - Supported formats: JPEG, PNG, WebP
    - Clear, well-lit photos focusing on affected areas

    **Personalization Features:**
    - Remembers your plant collection and care challenges
    - Adapts communication style to your experience level
    - Provides relevant context from previous conversations
    - Learns from your successful treatments and preferences
    """,
)
async def chat_with_assistant(
    request: ChatRequest,
    user_id: int = 1,  # TODO: Get from authentication
    db: AsyncSession = Depends(get_async_session),
) -> Union[ChatResponse, ChatError]:
    """
    Process chat message with personalized AI assistance.

    The enhanced assistant provides:
    1. **Personalized plant care advice** based on your history
    2. **Context-aware responses** using conversation memory
    3. **Image analysis** for plant health diagnosis
    4. **Learning capabilities** that improve over time
    5. **Persistent chat sessions** for continued conversations
    """
    try:
        # Validate input
        if not request.message.strip():
            raise HTTPException(
                status_code=400, detail="Message content cannot be empty"
            )

        # Get enhanced chat service
        chat_service = await get_chat_service(db)

        # Process chat request with personalization
        result = await chat_service.process_chat(request, user_id)

        # Check if result contains error
        if "error" in result:
            return ChatError(**result)

        # Return successful response
        return ChatResponse(**result)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        return ChatError(
            error="processing_error",
            message=f"Lỗi xử lý tin nhắn: {str(e)}",
            session_id=request.session_id,
        )


@router.get(
    "/sessions",
    summary="Get User Chat Sessions",
    description="Retrieve all chat sessions for the current user with metadata.",
)
async def get_user_sessions(
    limit: int = Query(20, ge=1, le=100),
    user_id: int = 1,  # TODO: Get from authentication
    db: AsyncSession = Depends(get_async_session),
):
    """Get user's chat sessions with plant context"""
    try:
        chat_service = await get_chat_service(db)
        sessions = await chat_service.get_user_sessions(user_id, limit)

        return {"sessions": sessions, "total": len(sessions)}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve sessions: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}",
    summary="Get Chat Session Messages",
    description="Retrieve all messages from a specific chat session.",
)
async def get_session_messages(
    session_id: str,
    limit: Optional[int] = Query(None, ge=1, le=200),
    user_id: int = 1,  # TODO: Get from authentication
    db: AsyncSession = Depends(get_async_session),
):
    """Get messages from a chat session"""
    try:
        chat_service = await get_chat_service(db)
        messages = await chat_service.get_session_messages(session_id, user_id, limit)

        if not messages:
            raise HTTPException(
                status_code=404, detail="Session not found or no messages"
            )

        return {"session_id": session_id, "messages": messages, "total": len(messages)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve messages: {str(e)}"
        )


@router.post(
    "/feedback",
    summary="Provide Message Feedback",
    description="Give feedback on assistant responses to improve personalization.",
)
async def add_message_feedback(
    message_id: int,
    rating: int = Query(..., ge=1, le=5),
    feedback_type: str = Query(
        ..., regex="^(helpful|not_helpful|incorrect|inappropriate|other)$"
    ),
    comment: Optional[str] = None,
    user_id: int = 1,  # TODO: Get from authentication
    db: AsyncSession = Depends(get_async_session),
):
    """Add feedback for a message to improve future responses"""
    try:
        chat_service = await get_chat_service(db)
        result = await chat_service.add_feedback(
            message_id=message_id,
            user_id=user_id,
            rating=rating,
            feedback_type=feedback_type,
            comment=comment,
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add feedback: {str(e)}")


@router.delete(
    "/sessions/{session_id}",
    summary="Delete Chat Session",
    description="Delete a chat session and its conversation history.",
)
async def delete_session(
    session_id: str,
    user_id: int = 1,  # TODO: Get from authentication
    db: AsyncSession = Depends(get_async_session),
):
    """Delete chat session and all its messages"""
    try:
        chat_service = await get_chat_service(db)

        # Verify session ownership
        session = await chat_service.chat_repo.get_session(session_id, user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Mark session as inactive (soft delete)
        await chat_service.chat_repo.update_session_context(
            session_id=session_id, user_preferences={"deleted": True}
        )

        return {
            "message": "Chat session deleted successfully",
            "session_id": session_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete session: {str(e)}"
        )
