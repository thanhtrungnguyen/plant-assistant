"""Chat API routes with LangGraph integration."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import require_user
from src.auth.models import User
from src.database.session import get_async_db
from src.chat.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat message request."""

    message: str
    conversation_id: Optional[str] = None
    plant_id: Optional[int] = None
    image_data: Optional[str] = None  # Base64 encoded image


class ChatResponse(BaseModel):
    """Chat message response."""

    message_id: int
    conversation_id: str
    response: str
    input_tokens: int
    output_tokens: int
    timestamp: str


class ConversationListResponse(BaseModel):
    """Conversation list item."""

    conversation_id: str
    plant_id: Optional[int]
    started_at: str
    last_message: Optional[str]
    last_message_time: str
    source: Optional[str]
    locale: Optional[str]


class MessageResponse(BaseModel):
    """Chat message."""

    message_id: str
    role: str
    content: str
    timestamp: str
    model: Optional[str]
    token_prompt: Optional[int]
    token_completion: Optional[int]
    image_url: Optional[str]


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_async_db),
) -> ChatResponse:
    """
    Send a message to the plant assistant and get a response.
    Creates a new conversation if conversation_id is not provided.
    """
    try:
        chat_service = ChatService(db)

        result = await chat_service.process_message(
            user_id=current_user.id,
            message=request.message,
            conversation_id=request.conversation_id,
            plant_id=request.plant_id,
            image_data=request.image_data,
        )

        return ChatResponse(
            message_id=result["message_id"],
            conversation_id=result["conversation_id"],
            response=result["response"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            timestamp=result["timestamp"].isoformat(),
        )

    except Exception as e:
        logger.error(f"Error in send_message endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        )


@router.get("/conversations", response_model=list[ConversationListResponse])
async def get_conversations(
    current_user: User = Depends(require_user), db: AsyncSession = Depends(get_async_db)
) -> list[ConversationListResponse]:
    """Get all conversations for the current user."""
    try:
        chat_service = ChatService(db)
        conversations = await chat_service.get_user_conversations(current_user.id)

        return [
            ConversationListResponse(
                conversation_id=conv["conversation_id"],
                plant_id=conv["plant_id"],
                started_at=conv["started_at"].isoformat(),
                last_message=conv["last_message"],
                last_message_time=conv["last_message_time"].isoformat(),
                source=conv["source"],
                locale=conv["locale"],
            )
            for conv in conversations
        ]

    except Exception as e:
        logger.error(f"Error in get_conversations endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations",
        )


@router.get(
    "/conversations/{conversation_id}/messages", response_model=list[MessageResponse]
)
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_async_db),
) -> list[MessageResponse]:
    """Get messages for a specific conversation."""
    try:
        chat_service = ChatService(db)
        messages = await chat_service.get_conversation_messages(
            user_id=current_user.id,
            conversation_id=conversation_id,
            limit=limit,
            offset=offset,
        )

        return [
            MessageResponse(
                message_id=msg["message_id"],
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"].isoformat(),
                model=msg["model"],
                token_prompt=msg["token_prompt"],
                token_completion=msg["token_completion"],
                image_url=msg["image_url"],
            )
            for msg in messages
        ]

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_conversation_messages endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages",
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_async_db),
) -> dict:
    """Delete a conversation and all its messages."""
    try:
        chat_service = ChatService(db)
        deleted = await chat_service.delete_conversation(
            user_id=current_user.id, conversation_id=conversation_id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        return {"message": "Conversation deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_conversation endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation",
        )


@router.get("/context", response_model=dict)
async def get_user_context_summary(
    current_user: User = Depends(require_user), db: AsyncSession = Depends(get_async_db)
) -> dict:
    """Get a summary of user's stored context across all conversations."""
    try:
        from src.chat.services.context_service import UserContextService

        context_service = UserContextService()
        context_summary = await context_service.get_user_context_summary(
            current_user.id
        )

        return context_summary

    except Exception as e:
        logger.error(f"Error in get_user_context_summary endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user context",
        )


@router.delete("/context")
async def delete_user_context(
    current_user: User = Depends(require_user), db: AsyncSession = Depends(get_async_db)
) -> dict:
    """Delete all stored context for the current user."""
    try:
        # This would require implementing a delete method in the context service
        # For now, return a placeholder response
        return {"message": "User context deletion not yet implemented"}

    except Exception as e:
        logger.error(f"Error in delete_user_context endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user context",
        )


@router.post("/context/refresh")
async def refresh_user_context(
    current_user: User = Depends(require_user), db: AsyncSession = Depends(get_async_db)
) -> dict:
    """Refresh user context by reprocessing recent conversations."""
    try:
        from src.chat.services.context_service import UserContextService

        context_service = UserContextService()

        # Get user's recent conversations and reprocess them
        chat_service = ChatService(db)
        conversations = await chat_service.get_user_conversations(current_user.id)

        processed_count = 0
        for conv in conversations[:5]:  # Process last 5 conversations
            try:
                await context_service.process_conversation_end(
                    db, current_user.id, conv["conversation_id"]
                )
                processed_count += 1
            except Exception as conv_error:
                logger.warning(
                    f"Failed to reprocess conversation {conv['conversation_id']}: {conv_error}"
                )

        return {
            "message": "Context refresh completed",
            "conversations_processed": processed_count,
            "total_conversations": len(conversations),
        }

    except Exception as e:
        logger.error(f"Error in refresh_user_context endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh user context",
        )
