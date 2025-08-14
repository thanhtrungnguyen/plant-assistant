"""Router for plant diagnosis endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.models import User
from src.database.session import get_db
from src.auth.dependencies import require_user
from src.diagnosis.schemas import DiagnoseRequest, DiagnoseResponse
from src.diagnosis.service import DiagnosisService

router = APIRouter(prefix="/plants/diagnose", tags=["plant-diagnosis"])


@router.post("/", response_model=DiagnoseResponse)
async def diagnose_plant(
    request: DiagnoseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    """Diagnose plant issues from symptoms and/or images."""
    service = DiagnosisService()
    diagnosis = await service.diagnose_plant(request)
    return diagnosis
