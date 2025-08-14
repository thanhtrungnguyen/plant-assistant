"""Dependencies for plants module."""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import require_user
from src.auth.models import User
from src.database.session import get_db
from src.plants.exceptions import PlantNotFoundError, PlantAccessDeniedError
from src.plants.models import Plant
from src.plants.service import PlantService


def get_plant_service(db: Session = Depends(get_db)) -> PlantService:
    """Get plant service instance."""
    return PlantService(db)


async def get_user_plant(
    plant_id: int,
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
) -> Plant:
    """Get a plant that belongs to the current user or is shared with them."""
    plant = await service.get_plant_with_access(plant_id, current_user.id)
    if not plant:
        raise PlantNotFoundError()
    return plant


async def get_user_owned_plant(
    plant_id: int,
    current_user: User = Depends(require_user),
    service: PlantService = Depends(get_plant_service),
) -> Plant:
    """Get a plant that is owned by the current user."""
    plant = await service.get_plant_by_id(plant_id)
    if not plant:
        raise PlantNotFoundError()
    if plant.user_id != current_user.id:
        raise PlantAccessDeniedError()
    return plant
