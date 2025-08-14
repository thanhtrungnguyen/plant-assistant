"""Main CRUD router for plants."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.auth.models import User
from src.database.session import get_db
from src.plants.constants import PlantStatus
from src.plants.dependencies import (
    get_current_user_from_request,
    get_plant_by_id,
)
from src.plants.schemas import (
    PlantCreate,
    PlantListParams,
    PlantListResponse,
    PlantResponse,
    PlantUpdate,
)
from src.plants.services import PlantsService

router = APIRouter(prefix="/plants", tags=["plants"])


@router.post("/", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
async def create_plant(
    plant_data: PlantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Create a new plant for the current user."""
    service = PlantsService(db)
    plant = service.create_plant(plant_data, current_user)

    # Convert to response format with computed fields
    return PlantResponse(
        **plant.__dict__,
        status=PlantStatus.UNKNOWN,
        photo_count=0,
        last_care_date=None,
        next_reminder_date=None,
    )


@router.get("/", response_model=PlantListResponse)
async def get_plants(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    species_id: int = Query(None),
    is_archived: bool = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Get paginated list of user's plants."""
    # Validate and create params
    params = PlantListParams(
        page=page,
        size=size,
        search=search,
        species_id=species_id,
        is_archived=is_archived,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    service = PlantsService(db)
    plants, total = service.get_user_plants(current_user, params)

    pages = (total + size - 1) // size  # Ceiling division

    return PlantListResponse(
        plants=plants,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{plant_id}", response_model=PlantResponse)
async def get_plant(
    plant=Depends(get_plant_by_id),
):
    """Get a specific plant by ID."""
    return PlantResponse(
        **plant.__dict__,
        status=PlantStatus.UNKNOWN,  # This would be computed in a real service
        photo_count=0,
        last_care_date=None,
        next_reminder_date=None,
    )


@router.put("/{plant_id}", response_model=PlantResponse)
async def update_plant(
    plant_id: int,
    plant_data: PlantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Update a plant."""
    service = PlantsService(db)
    updated_plant = service.update_plant(plant_id, plant_data, current_user)

    return PlantResponse(
        **updated_plant.__dict__,
        status=PlantStatus.UNKNOWN,
        photo_count=0,
        last_care_date=None,
        next_reminder_date=None,
    )


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Delete (archive) a plant."""
    service = PlantsService(db)
    service.delete_plant(plant_id, current_user)
