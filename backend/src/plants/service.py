"""Service layer for plants module."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from src.plants.models import Plant, PlantPhoto, PlantShare
from src.plants.schemas import (
    PlantCreate,
    PlantUpdate,
    PlantListParams,
    PlantPhotoCreate,
    PlantShareCreate,
)
from src.plants.exceptions import (
    PlantNotFoundError,
    PlantAccessDeniedError,
    PlantPhotoNotFoundError,
    PlantShareNotFoundError,
)


class PlantService:
    """Service class for plant operations."""

    def __init__(self, db: Session):
        self.db = db

    async def create_plant(self, plant_data: PlantCreate, user_id: int) -> Plant:
        """Create a new plant."""
        plant = Plant(user_id=user_id, **plant_data.model_dump(exclude_unset=True))
        self.db.add(plant)
        self.db.commit()
        self.db.refresh(plant)
        return plant

    async def get_plant_by_id(self, plant_id: int) -> Optional[Plant]:
        """Get a plant by its ID."""
        return self.db.query(Plant).filter(Plant.id == plant_id).first()

    async def get_plant_with_access(
        self, plant_id: int, user_id: int
    ) -> Optional[Plant]:
        """Get a plant that the user owns or has access to via sharing."""
        # First check if user owns the plant
        plant = (
            self.db.query(Plant)
            .filter(Plant.id == plant_id, Plant.user_id == user_id)
            .first()
        )

        if plant:
            return plant

        # Check if plant is shared with the user
        shared_plant = (
            self.db.query(Plant)
            .join(PlantShare)
            .filter(Plant.id == plant_id, PlantShare.user_id == user_id)
            .first()
        )

        return shared_plant

    async def get_user_plants(
        self, user_id: int, params: PlantListParams
    ) -> tuple[List[Plant], int]:
        """Get paginated list of user's plants."""
        query = self.db.query(Plant).filter(Plant.user_id == user_id)

        # Apply filters
        if params.search:
            query = query.filter(
                or_(
                    Plant.nickname.ilike(f"%{params.search}%"),
                    Plant.location_text.ilike(f"%{params.search}%"),
                    Plant.notes.ilike(f"%{params.search}%"),
                )
            )

        if params.status:
            # Status filtering not implemented in current model
            pass

        if params.archived is not None:
            query = query.filter(Plant.is_archived == params.archived)

        if params.species_id:
            query = query.filter(Plant.species_id == params.species_id)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        query = query.order_by(desc(Plant.updated_at))
        offset = (params.page - 1) * params.page_size
        plants = query.offset(offset).limit(params.page_size).all()

        return plants, total

    async def update_plant(
        self, plant_id: int, plant_data: PlantUpdate, user_id: int
    ) -> Plant:
        """Update a plant."""
        plant = await self.get_plant_by_id(plant_id)
        if not plant:
            raise PlantNotFoundError()

        if plant.user_id != user_id:
            raise PlantAccessDeniedError()

        update_data = plant_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plant, field, value)

        plant.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(plant)
        return plant

    async def delete_plant(self, plant_id: int, user_id: int) -> bool:
        """Delete a plant."""
        plant = await self.get_plant_by_id(plant_id)
        if not plant:
            raise PlantNotFoundError()

        if plant.user_id != user_id:
            raise PlantAccessDeniedError()

        self.db.delete(plant)
        self.db.commit()
        return True

    async def add_plant_photo(
        self, plant_id: int, photo_data: PlantPhotoCreate, user_id: int
    ) -> PlantPhoto:
        """Add a photo to a plant."""
        plant = await self.get_plant_with_access(plant_id, user_id)
        if not plant:
            raise PlantNotFoundError()

        photo = PlantPhoto(plant_id=plant_id, **photo_data.model_dump())
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        return photo

    async def get_plant_photos(self, plant_id: int, user_id: int) -> List[PlantPhoto]:
        """Get all photos for a plant."""
        plant = await self.get_plant_with_access(plant_id, user_id)
        if not plant:
            raise PlantNotFoundError()

        return (
            self.db.query(PlantPhoto)
            .filter(PlantPhoto.plant_id == plant_id)
            .order_by(desc(PlantPhoto.created_at))
            .all()
        )

    async def delete_plant_photo(self, photo_id: int, user_id: int) -> bool:
        """Delete a plant photo."""
        photo = self.db.query(PlantPhoto).filter(PlantPhoto.id == photo_id).first()
        if not photo:
            raise PlantPhotoNotFoundError()

        # Check if user has access to the plant
        plant = await self.get_plant_with_access(photo.plant_id, user_id)
        if not plant:
            raise PlantAccessDeniedError()

        self.db.delete(photo)
        self.db.commit()
        return True

    async def share_plant(
        self, plant_id: int, share_data: PlantShareCreate, owner_id: int
    ) -> PlantShare:
        """Share a plant with another user."""
        plant = await self.get_plant_by_id(plant_id)
        if not plant:
            raise PlantNotFoundError()

        if plant.user_id != owner_id:
            raise PlantAccessDeniedError()

        # Check if already shared
        existing_share = (
            self.db.query(PlantShare)
            .filter(
                PlantShare.plant_id == plant_id,
                PlantShare.user_id == share_data.user_id,
            )
            .first()
        )

        if existing_share:
            # Update existing share
            existing_share.role = share_data.role
            self.db.commit()
            return existing_share

        # Create new share
        share = PlantShare(plant_id=plant_id, **share_data.model_dump())
        self.db.add(share)
        self.db.commit()
        self.db.refresh(share)
        return share

    async def get_plant_shares(self, plant_id: int, owner_id: int) -> List[PlantShare]:
        """Get all shares for a plant."""
        plant = await self.get_plant_by_id(plant_id)
        if not plant:
            raise PlantNotFoundError()

        if plant.user_id != owner_id:
            raise PlantAccessDeniedError()

        return self.db.query(PlantShare).filter(PlantShare.plant_id == plant_id).all()

    async def remove_plant_share(
        self, plant_id: int, shared_user_id: int, owner_id: int
    ) -> bool:
        """Remove a plant share."""
        plant = await self.get_plant_by_id(plant_id)
        if not plant:
            raise PlantNotFoundError()

        if plant.user_id != owner_id:
            raise PlantAccessDeniedError()

        share = (
            self.db.query(PlantShare)
            .filter(
                PlantShare.plant_id == plant_id, PlantShare.user_id == shared_user_id
            )
            .first()
        )

        if not share:
            raise PlantShareNotFoundError()

        self.db.delete(share)
        self.db.commit()
        return True

    async def update_care_tracking(
        self, plant_id: int, care_type: str, user_id: int
    ) -> Plant:
        """Update care tracking for a plant (via ai_metrics_json)."""
        plant = await self.get_plant_with_access(plant_id, user_id)
        if not plant:
            raise PlantNotFoundError()

        now = datetime.utcnow()

        # Store care tracking in ai_metrics_json since no dedicated fields exist
        if not plant.ai_metrics_json:
            plant.ai_metrics_json = {}

        if "care_log" not in plant.ai_metrics_json:
            plant.ai_metrics_json["care_log"] = {}

        if care_type == "water":
            plant.ai_metrics_json["care_log"]["last_watered"] = now.isoformat()
        elif care_type == "fertilize":
            plant.ai_metrics_json["care_log"]["last_fertilized"] = now.isoformat()

        plant.updated_at = now
        self.db.commit()
        self.db.refresh(plant)
        return plant

    async def generate_plant_insights(
        self, plant_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Generate AI insights for a plant."""
        plant = await self.get_plant_with_access(plant_id, user_id)
        if not plant:
            raise PlantNotFoundError()

        # This would integrate with AI services
        # For now, return mock insights
        insights = {
            "growth_stage": "mature",
            "health_score": 85,
            "care_recommendations": [
                "Water every 3-4 days",
                "Increase light exposure",
                "Consider repotting in spring",
            ],
            "next_care_actions": [
                {
                    "action": "water",
                    "due_date": datetime.utcnow().isoformat(),
                    "priority": "medium",
                }
            ],
        }

        # Update plant's AI metrics
        plant.ai_metrics_json = insights
        plant.updated_at = datetime.utcnow()
        self.db.commit()

        return insights
