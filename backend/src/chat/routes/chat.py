"""
Chat API Routes

Provides conversational interface for plant care assistance with image analysis.
"""

from typing import Union
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer

from ..schemas import ChatRequest, ChatResponse, ChatError
from ..services.enhanced_chat_service import EnhancedChatService


async def get_enhanced_chat_service() -> EnhancedChatService:
    """Dependency to get enhanced chat service instance"""
    return EnhancedChatService()


router = APIRouter(prefix="/chat", tags=["Plant Care Chat"])
security = HTTPBearer()


@router.post(
    "/",
    response_model=Union[ChatResponse, ChatError],
    summary="Chat with Plant Care Assistant",
    description="""
    Send a message to the plant care AI assistant. Features include:

    - **Text conversations**: Ask questions about plant care, watering, lighting, fertilizing
    - **Image analysis**: Upload plant images for health diagnosis and species identification
    - **Session management**: Maintain conversation history for context
    - **Suggestions**: Get relevant follow-up questions

    **Usage Examples:**
    - Text only: "Cây của tôi bị vàng lá, nguyên nhân gì?"
    - With image: Upload image + "Cây này có bệnh gì không?"
    - Follow-up: Continue conversation with session_id

    **Image Requirements:**
    - Base64 encoded string
    - Supported formats: JPEG, PNG, WebP
    - Clear, well-lit photos of plants
    - Focus on affected areas for diagnosis
    """,
)
async def chat_with_assistant(
    request: ChatRequest,
    chat_service: EnhancedChatService = Depends(get_enhanced_chat_service),
) -> Union[ChatResponse, ChatError]:
    """
    Process chat message with optional image analysis.

    The assistant can:
    1. Answer general plant care questions
    2. Analyze plant images for health issues
    3. Provide specific treatment recommendations
    4. Maintain conversation context across messages
    """
    try:
        # Validate input
        if not request.message.strip():
            raise HTTPException(
                status_code=400, detail="Message content cannot be empty"
            )

        # Process chat request
        result = await chat_service.process_chat(request)

        # Return result directly (it should be ChatResponse already)
        return result

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
    "/sessions/{session_id}",
    summary="Get Chat Session Info",
    description="Retrieve information about a specific chat session including message count and metadata.",
)
async def get_session_info(
    session_id: str, chat_service: EnhancedChatService = Depends(get_enhanced_chat_service)
):
    """Get chat session information"""
    if session_id in chat_service._sessions:
        session_data = chat_service._sessions[session_id]
        return {
            "session_id": session_id,
            "created_at": session_data["created_at"],
            "updated_at": session_data["updated_at"],
            "message_count": session_data["message_count"],
            "active": True,
        }
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@router.delete(
    "/sessions/{session_id}",
    summary="Delete Chat Session",
    description="Delete a chat session and its conversation history.",
)
async def delete_session(
    session_id: str, chat_service: EnhancedChatService = Depends(get_enhanced_chat_service)
):
    """Delete chat session"""
    if session_id in chat_service._sessions:
        del chat_service._sessions[session_id]
        return {"message": "Session deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")
