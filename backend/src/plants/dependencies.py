"""Dependencies for the plants module."""

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.auth.dependencies import require_user
from src.auth.models import User
from src.database.session import get_db
from src.plants.exceptions import PlantAccessDeniedException, PlantNotFoundException
from src.plants.models.plants import Plant


def get_current_user_from_request(request: Request) -> User:
    """Get current user from request."""
    return require_user(request)


async def get_plant_by_id(
    plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
) -> Plant:
    """Get a plant by ID and verify user access."""
    plant = db.query(Plant).filter(Plant.id == plant_id).first()

    if not plant:
        raise PlantNotFoundException(plant_id)

    if plant.user_id != current_user.id:
        raise PlantAccessDeniedException(plant_id)

    return plant


def get_user_plants_query(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Get base query for user's plants."""
    return db.query(Plant).filter(Plant.user_id == current_user.id)


class PaginationDep:
    """Dependency for pagination parameters."""

    def __init__(self, default_size: int = 20, max_size: int = 100):
        self.default_size = default_size
        self.max_size = max_size

    def __call__(
        self,
        page: int = 1,
        size: int | None = None,
    ) -> tuple[int, int]:
        """Return validated page and size parameters."""
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Page must be >= 1"
            )

        if size is None:
            size = self.default_size
        elif size < 1 or size > self.max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Size must be between 1 and {self.max_size}",
            )

        return page, size


# Convenience instances
pagination = PaginationDep()
large_pagination = PaginationDep(default_size=50, max_size=500)


def calculate_offset_limit(page: int, size: int) -> tuple[int, int]:
    """Calculate SQL offset and limit from page and size."""
    offset = (page - 1) * size
    limit = size
    return offset, limit


def get_plants_service(db: Session = Depends(get_db)):
    """Dependency to get plants service instance."""
    # This will import the service when needed to avoid circular imports
    from .services import PlantsService

    return PlantsService(db)


def get_identification_service():
    """Dependency to get identification service instance."""
    from .services.identification import IdentificationService

    return IdentificationService()


def get_reminder_service(db: Session = Depends(get_db)):
    """Dependency to get reminder service instance."""
    from .services.reminders import ReminderService

    return ReminderService(db)
