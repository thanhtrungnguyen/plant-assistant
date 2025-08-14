"""Router for plant identification endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.models import User
from src.database.session import get_db
from src.plants.dependencies import get_current_user_from_request
from src.plants.schemas import IdentifyRequest, IdentifyResponse
from src.plants.services import IdentificationService

router = APIRouter(prefix="/plants/identify", tags=["plant-identification"])


@router.post("/", response_model=IdentifyResponse)
async def identify_plant(
    request: IdentifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Identify a plant from images and/or description."""
    service = IdentificationService()
    result = await service.identify_plant(request)
    return result
