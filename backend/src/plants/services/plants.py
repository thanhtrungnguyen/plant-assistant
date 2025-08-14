"""Main service layer for the plants module."""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from src.auth.models import User
from src.plants.constants import PlantStatus
from src.plants.exceptions import PlantNotFoundException
from src.plants.models.plants import Plant, PlantPhoto
from src.plants.models.reminders import Reminder
from src.plants.schemas import (
    DashboardStats,
    PlantCreate,
    PlantListParams,
    PlantResponse,
    PlantUpdate,
)


class PlantsService:
    """Service class for plant-related operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_plant(self, plant_data: PlantCreate, user: User) -> Plant:
        """Create a new plant for the user."""
        plant = Plant(
            user_id=user.id,
            nickname=plant_data.nickname,
            species_id=plant_data.species_id,
            location_text=plant_data.location_text,
            notes=plant_data.notes,
            latitude=plant_data.latitude,
            longitude=plant_data.longitude,
            acquisition_date=plant_data.acquisition_date,
        )

        self.db.add(plant)
        self.db.commit()
        self.db.refresh(plant)

        return plant

    def get_plant_by_id(self, plant_id: int, user: User) -> Plant:
        """Get a plant by ID, ensuring user access."""
        plant = (
            self.db.query(Plant)
            .filter(Plant.id == plant_id, Plant.user_id == user.id)
            .first()
        )

        if not plant:
            raise PlantNotFoundException(plant_id)

        return plant

    def update_plant(self, plant_id: int, plant_data: PlantUpdate, user: User) -> Plant:
        """Update a plant."""
        plant = self.get_plant_by_id(plant_id, user)

        # Update fields if provided
        update_data = plant_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plant, field, value)

        self.db.commit()
        self.db.refresh(plant)

        return plant

    def delete_plant(self, plant_id: int, user: User) -> bool:
        """Delete a plant (soft delete by archiving)."""
        plant = self.get_plant_by_id(plant_id, user)
        plant.is_archived = True

        self.db.commit()

        return True

    def get_user_plants(
        self,
        user: User,
        params: PlantListParams,
    ) -> Tuple[List[PlantResponse], int]:
        """Get paginated list of user's plants."""
        query = self.db.query(Plant).filter(Plant.user_id == user.id)

        # Apply filters
        if params.search:
            search_term = f"%{params.search}%"
            query = query.filter(
                or_(
                    Plant.nickname.ilike(search_term),
                    Plant.location_text.ilike(search_term),
                    Plant.notes.ilike(search_term),
                )
            )

        if params.species_id is not None:
            query = query.filter(Plant.species_id == params.species_id)

        if params.is_archived is not None:
            query = query.filter(Plant.is_archived == params.is_archived)
        else:
            # Default to showing non-archived plants
            query = query.filter(~Plant.is_archived)

        # Apply sorting
        if params.sort_by == "nickname":
            order_col = Plant.nickname
        elif params.sort_by == "updated_at":
            order_col = Plant.updated_at
        elif params.sort_by == "acquisition_date":
            order_col = Plant.acquisition_date
        else:  # created_at
            order_col = Plant.created_at

        if params.sort_order == "desc":
            order_col = order_col.desc()

        query = query.order_by(order_col)

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        offset = (params.page - 1) * params.size
        plants = query.offset(offset).limit(params.size).all()

        # Convert to response objects with additional data
        plant_responses = []
        for plant in plants:
            # Get photo count
            photo_count = (
                self.db.query(func.count(PlantPhoto.id))
                .filter(PlantPhoto.plant_id == plant.id)
                .scalar()
            )

            # Get last care date (from reminders that were completed)
            last_care_date = (
                self.db.query(func.max(Reminder.completed_at))
                .filter(
                    Reminder.plant_id == plant.id,
                    Reminder.is_completed.is_(True),
                )
                .scalar()
            )

            # Get next reminder date
            next_reminder = (
                self.db.query(Reminder.next_due_date)
                .filter(
                    Reminder.plant_id == plant.id,
                    ~Reminder.is_completed,
                    Reminder.next_due_date >= datetime.utcnow(),
                )
                .order_by(Reminder.next_due_date)
                .first()
            )
            next_reminder_date = next_reminder[0] if next_reminder else None

            # Determine plant status (simplified logic)
            status = self._determine_plant_status(
                plant, last_care_date, next_reminder_date
            )

            plant_response = PlantResponse(
                **plant.__dict__,
                status=status,
                photo_count=photo_count,
                last_care_date=last_care_date,
                next_reminder_date=next_reminder_date,
            )
            plant_responses.append(plant_response)

        return plant_responses, total

    def get_dashboard_stats(self, user: User) -> DashboardStats:
        """Get dashboard statistics for the user."""
        now = datetime.utcnow()

        # Total plants (non-archived)
        total_plants = (
            self.db.query(func.count(Plant.id))
            .filter(Plant.user_id == user.id, ~Plant.is_archived)
            .scalar()
        )

        # For now, use simplified logic for health status
        # In a real app, this would be more sophisticated
        healthy_plants = max(0, total_plants - 2)  # Placeholder
        plants_needing_attention = min(2, total_plants)  # Placeholder

        # Overdue reminders
        overdue_reminders = (
            self.db.query(func.count(Reminder.id))
            .join(Plant)
            .filter(
                Plant.user_id == user.id,
                ~Reminder.is_completed,
                Reminder.next_due_date < now,
            )
            .scalar()
        )

        # Reminders today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        reminders_today = (
            self.db.query(func.count(Reminder.id))
            .join(Plant)
            .filter(
                Plant.user_id == user.id,
                ~Reminder.is_completed,
                Reminder.next_due_date.between(today_start, today_end),
            )
            .scalar()
        )

        # Reminders this week (next 7 days)
        week_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        week_end = week_end + timedelta(days=7)

        reminders_this_week = (
            self.db.query(func.count(Reminder.id))
            .join(Plant)
            .filter(
                Plant.user_id == user.id,
                ~Reminder.is_completed,
                Reminder.next_due_date.between(now, week_end),
            )
            .scalar()
        )

        return DashboardStats(
            total_plants=total_plants,
            healthy_plants=healthy_plants,
            plants_needing_attention=plants_needing_attention,
            overdue_reminders=overdue_reminders,
            reminders_today=reminders_today,
            reminders_this_week=reminders_this_week,
        )

    def _determine_plant_status(
        self,
        plant: Plant,
        last_care_date: Optional[datetime],
        next_reminder_date: Optional[datetime],
    ) -> PlantStatus:
        """Determine the plant's status based on care history and upcoming reminders."""
        now = datetime.utcnow()

        # If there are overdue reminders, plant needs attention
        if next_reminder_date and next_reminder_date < now:
            return PlantStatus.WARNING

        # If no care in the last 30 days, might be concerning
        if last_care_date:
            days_since_care = (now - last_care_date).days
            if days_since_care > 30:
                return PlantStatus.WARNING
            elif days_since_care > 60:
                return PlantStatus.CRITICAL

        # If plant has AI metrics indicating issues
        if plant.ai_metrics_json:
            # This would contain more sophisticated health analysis
            health_score = plant.ai_metrics_json.get("health_score", 0.5)
            if health_score < 0.3:
                return PlantStatus.CRITICAL
            elif health_score < 0.6:
                return PlantStatus.WARNING

        return PlantStatus.HEALTHY
