"""Router for plant care advice endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import require_user
from src.auth.models import User
from src.care.schemas import CareRequest, CareResponse
from src.care.service import CareAdviceService
from src.database.session import get_db

router = APIRouter(prefix="/plants/care", tags=["plant-care"])


@router.post("/advice", response_model=CareResponse)
async def get_care_advice(
    request: CareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Get personalized care advice for a plant."""
    service = CareAdviceService()
    advice = await service.generate_care_advice(request)
    return advice
