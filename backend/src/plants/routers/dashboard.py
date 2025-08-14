"""Router for dashboard and analytics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.models import User
from src.database.session import get_db
from src.plants.dependencies import get_current_user_from_request
from src.plants.schemas import DashboardResponse
from src.plants.services import PlantsService

router = APIRouter(prefix="/plants/dashboard", tags=["plant-dashboard"])


@router.get("/stats", response_model=DashboardResponse)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Get dashboard data for the current user."""
    service = PlantsService(db)
    stats = service.get_dashboard_stats(current_user)

    # For now, return empty lists for the detailed data
    # In a full implementation, these would be populated
    return DashboardResponse(
        stats=stats,
        recent_plants=[],
        upcoming_reminders=[],
        recent_photos=[],
    )
