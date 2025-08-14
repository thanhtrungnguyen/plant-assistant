"""Router for conversational chat endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import require_user
from src.auth.models import User
from src.conversations.schemas import ChatRequest, ChatResponse
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
