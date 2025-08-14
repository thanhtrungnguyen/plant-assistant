"""Router for plant care advice endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.models import User
from src.database.session import get_db
from src.plants.dependencies import get_current_user_from_request
from src.plants.schemas import CareRequest, CareResponse
from src.plants.services import CareAdviceService

router = APIRouter(prefix="/plants/care", tags=["plant-care"])


@router.post("/advice", response_model=CareResponse)
async def get_care_advice(
    request: CareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Get personalized care advice for a plant."""
    service = CareAdviceService()
    advice = await service.generate_care_advice(request)
    return advice
