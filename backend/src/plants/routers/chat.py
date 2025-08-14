"""Router for conversational chat endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.models import User
from src.database.session import get_db
from src.plants.dependencies import get_current_user_from_request
from src.plants.schemas import ChatRequest, ChatResponse
from src.plants.services import ConversationalService

router = APIRouter(prefix="/plants/chat", tags=["plant-chat"])


@router.post("/", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Chat with the plant care assistant."""
    service = ConversationalService()
    response = await service.process_chat_message(request)
    return response
