"""API routes for plants module."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List

from src.auth.dependencies import require_user
from src.auth.models import User
from src.plants.dependencies import (
    get_plant_service,
    get_user_plant,
    get_user_owned_plant,
)
from src.plants.models import Plant
from src.plants.schemas import (
    PlantCreate,
    PlantUpdate,
    PlantResponse,
    PlantListResponse,
    PlantListParams,
    PlantPhotoCreate,
    PlantPhotoResponse,
    PlantShareCreate,
    PlantShareResponse,
)
from src.plants.service import PlantService

router = APIRouter(prefix="/plants", tags=["plants"])


@router.post("/", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
async def create_plant(
    plant_data: PlantCreate,
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
) -> PlantResponse:
    """Create a new plant."""
    plant = await service.create_plant(plant_data, current_user.id)
    return PlantResponse.model_validate(plant)


@router.get("/", response_model=PlantListResponse)
async def list_plants(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str = Query(None, description="Search term"),
    archived: bool = Query(None, description="Filter by archived status"),
    species_id: int = Query(None, description="Filter by species"),
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
) -> PlantListResponse:
    """Get paginated list of user's plants."""
    params = PlantListParams(
        page=page,
        page_size=page_size,
        search=search,
        status=None,  # Status filtering not implemented in current model
        archived=archived,
        species_id=species_id,
    )

    plants, total = await service.get_user_plants(current_user.id, params)
    total_pages = (total + params.page_size - 1) // params.page_size

    return PlantListResponse(
        plants=[PlantResponse.model_validate(plant) for plant in plants],
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
    )


@router.get("/{plant_id}", response_model=PlantResponse)
async def get_plant(plant: Plant = Depends(get_user_plant)) -> PlantResponse:
    """Get a specific plant."""
    return PlantResponse.model_validate(plant)


@router.put("/{plant_id}", response_model=PlantResponse)
async def update_plant(
    plant_data: PlantUpdate,
    plant: Plant = Depends(get_user_owned_plant),
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
) -> PlantResponse:
    """Update a plant."""
    updated_plant = await service.update_plant(plant.id, plant_data, current_user.id)
    return PlantResponse.model_validate(updated_plant)


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    plant: Plant = Depends(get_user_owned_plant),
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
):
    """Delete a plant."""
    await service.delete_plant(plant.id, current_user.id)


@router.post(
    "/{plant_id}/photos",
    response_model=PlantPhotoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_plant_photo(
    plant_id: int,
    photo_data: PlantPhotoCreate,
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
) -> PlantPhotoResponse:
    """Add a photo to a plant."""
    photo = await service.add_plant_photo(plant_id, photo_data, current_user.id)
    return PlantPhotoResponse.model_validate(photo)


@router.get("/{plant_id}/photos", response_model=List[PlantPhotoResponse])
async def get_plant_photos(
    plant_id: int,
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
) -> List[PlantPhotoResponse]:
    """Get all photos for a plant."""
    photos = await service.get_plant_photos(plant_id, current_user.id)
    return [PlantPhotoResponse.model_validate(photo) for photo in photos]


@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant_photo(
    photo_id: int,
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
):
    """Delete a plant photo."""
    await service.delete_plant_photo(photo_id, current_user.id)


@router.post(
    "/{plant_id}/share",
    response_model=PlantShareResponse,
    status_code=status.HTTP_201_CREATED,
)
async def share_plant(
    plant_id: int,
    share_data: PlantShareCreate,
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
) -> PlantShareResponse:
    """Share a plant with another user."""
    share = await service.share_plant(plant_id, share_data, current_user.id)
    return PlantShareResponse.model_validate(share)


@router.get("/{plant_id}/shares", response_model=List[PlantShareResponse])
async def get_plant_shares(
    plant_id: int,
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
) -> List[PlantShareResponse]:
    """Get all shares for a plant."""
    shares = await service.get_plant_shares(plant_id, current_user.id)
    return [PlantShareResponse.model_validate(share) for share in shares]


@router.delete("/{plant_id}/shares/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_plant_share(
    plant_id: int,
    user_id: int,
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
):
    """Remove a plant share."""
    await service.remove_plant_share(plant_id, user_id, current_user.id)


@router.post("/{plant_id}/care/{care_type}", response_model=PlantResponse)
async def update_care_tracking(
    plant_id: int,
    care_type: str,
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
) -> PlantResponse:
    """Update care tracking for a plant (water, fertilize, etc.)."""
    if care_type not in ["water", "fertilize"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid care type. Must be 'water' or 'fertilize'",
        )

    updated_plant = await service.update_care_tracking(
        plant_id, care_type, current_user.id
    )
    return PlantResponse.model_validate(updated_plant)


@router.get("/{plant_id}/insights", response_model=dict)
async def get_plant_insights(
    plant_id: int,
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
) -> dict:
    """Generate AI insights for a plant."""
    insights = await service.generate_plant_insights(plant_id, current_user.id)
    return insights
