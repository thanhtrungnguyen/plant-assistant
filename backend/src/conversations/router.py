"""Router for conversational chat endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.auth.dependencies import require_user
from src.auth.models import User
from src.conversations.schemas import ChatRequest, ChatResponse, ChatHistoryResponse
from src.conversations.service import ConversationalService
from src.database.session import get_db

router = APIRouter(prefix="/plants/chat", tags=["plant-chat"])


@router.post("/", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Chat with the plant care assistant."""
    service = ConversationalService()
    response = await service.process_chat_message(request)
    return response


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = Query(10, ge=1, le=50, description="Number of sessions to retrieve"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get chat history for the current user."""
    service = ConversationalService()
    response = await service.get_chat_history(current_user.id, limit, offset, db)
    return response
