"""Reminder service for plant care scheduling."""

from datetime import datetime, timedelta
from typing import List, Tuple

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.auth.models import User
from src.plants.models import Plant
from src.reminders.models import Reminder
from src.reminders.exceptions import ReminderNotFoundException
from src.reminders.schemas import (
    ReminderCreate,
    ReminderListParams,
    ReminderResponse,
    ReminderUpdate,
)


class ReminderService:
    """Service for managing plant care reminders."""

    def __init__(self, db: Session):
        self.db = db

    def create_reminder(self, reminder_data: ReminderCreate, user: User) -> Reminder:
        """Create a new reminder for a plant."""
        # Verify plant belongs to user
        plant = (
            self.db.query(Plant)
            .filter(Plant.id == reminder_data.plant_id, Plant.user_id == user.id)
            .first()
        )

        if not plant:
            from src.plants.exceptions import PlantNotFoundError

            raise PlantNotFoundError(
                f"Plant with ID {reminder_data.plant_id} not found"
            )

        reminder = Reminder(
            plant_id=reminder_data.plant_id,
            user_id=user.id,
            title=reminder_data.title,
            description=reminder_data.description,
            task_type=reminder_data.reminder_type.value,
            priority=reminder_data.priority.value,
            next_due_date=reminder_data.next_due_date,
            is_recurring=reminder_data.is_recurring,
            cron_expression=reminder_data.cron_expression,
        )

        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)

        return reminder

    def get_reminder_by_id(self, reminder_id: int, user: User) -> Reminder:
        """Get a reminder by ID, ensuring user access."""
        reminder = (
            self.db.query(Reminder)
            .join(Plant)
            .filter(
                Reminder.id == reminder_id,
                Plant.user_id == user.id,
            )
            .first()
        )

        if not reminder:
            raise ReminderNotFoundException(f"Reminder with ID {reminder_id} not found")

        return reminder

    def update_reminder(
        self, reminder_id: int, reminder_data: ReminderUpdate, user: User
    ) -> Reminder:
        """Update a reminder."""
        reminder = self.get_reminder_by_id(reminder_id, user)

        # Update fields if provided
        update_data = reminder_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "reminder_type" and value is not None:
                setattr(reminder, "task_type", value.value)
            elif field == "priority" and value is not None:
                setattr(reminder, field, value.value)
            else:
                setattr(reminder, field, value)

        # Handle completion
        if reminder_data.is_completed is not None:
            if reminder_data.is_completed and not reminder.is_completed:
                reminder.completed_at = datetime.utcnow()
                # If recurring, calculate next due date
                if reminder.is_recurring and reminder.cron_expression:
                    reminder.next_due_date = self._calculate_next_due_date(
                        reminder.cron_expression
                    )
                    reminder.is_completed = False
                    reminder.completed_at = None
            elif not reminder_data.is_completed:
                reminder.completed_at = None

        self.db.commit()
        self.db.refresh(reminder)

        return reminder

    def delete_reminder(self, reminder_id: int, user: User) -> bool:
        """Delete a reminder."""
        reminder = self.get_reminder_by_id(reminder_id, user)
        self.db.delete(reminder)
        self.db.commit()
        return True

    def get_user_reminders(
        self, user: User, params: ReminderListParams
    ) -> Tuple[List[ReminderResponse], int]:
        """Get paginated list of user's reminders."""
        query = self.db.query(Reminder).join(Plant).filter(Plant.user_id == user.id)

        # Apply filters
        if params.plant_id is not None:
            query = query.filter(Reminder.plant_id == params.plant_id)

        if params.reminder_type is not None:
            query = query.filter(Reminder.task_type == params.reminder_type.value)

        if params.priority is not None:
            query = query.filter(Reminder.priority == params.priority.value)

        if params.is_completed is not None:
            query = query.filter(Reminder.is_completed == params.is_completed)

        if params.overdue_only:
            now = datetime.utcnow()
            query = query.filter(
                and_(
                    ~Reminder.is_completed,
                    Reminder.next_due_date < now,
                )
            )

        # Apply sorting
        if params.sort_by == "created_at":
            order_col = Reminder.created_at
        elif params.sort_by == "priority":
            # Custom priority ordering (high, medium, low)
            order_col = func.case(
                (Reminder.priority == "high", 1),
                (Reminder.priority == "medium", 2),
                (Reminder.priority == "low", 3),
                else_=4,
            )
        else:  # next_due_date
            order_col = Reminder.next_due_date

        if params.sort_order == "desc":
            order_col = order_col.desc()

        query = query.order_by(order_col)

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        offset = (params.page - 1) * params.size
        reminders = query.offset(offset).limit(params.size).all()

        # Convert to response objects
        reminder_responses = []
        now = datetime.utcnow()

        for reminder in reminders:
            # Get plant nickname
            plant = self.db.query(Plant).filter(Plant.id == reminder.plant_id).first()
            plant_nickname = plant.nickname if plant else None

            # Calculate if overdue and days until due
            is_overdue = not reminder.is_completed and reminder.next_due_date < now

            days_until_due = None
            if not reminder.is_completed:
                delta = reminder.next_due_date - now
                days_until_due = delta.days

            reminder_response = ReminderResponse(
                **reminder.__dict__,
                plant_nickname=plant_nickname,
                is_overdue=is_overdue,
                days_until_due=days_until_due,
            )
            reminder_responses.append(reminder_response)

        return reminder_responses, total

    def get_upcoming_reminders(
        self, user: User, days_ahead: int = 7
    ) -> List[ReminderResponse]:
        """Get upcoming reminders for the next N days."""
        now = datetime.utcnow()
        end_date = now + timedelta(days=days_ahead)

        reminders = (
            self.db.query(Reminder)
            .join(Plant)
            .filter(
                Plant.user_id == user.id,
                ~Reminder.is_completed,
                Reminder.next_due_date.between(now, end_date),
            )
            .order_by(Reminder.next_due_date)
            .all()
        )

        # Convert to response objects
        reminder_responses = []
        for reminder in reminders:
            plant = self.db.query(Plant).filter(Plant.id == reminder.plant_id).first()
            plant_nickname = plant.nickname if plant else None

            delta = reminder.next_due_date - now
            days_until_due = delta.days
            is_overdue = days_until_due < 0

            reminder_response = ReminderResponse(
                **reminder.__dict__,
                plant_nickname=plant_nickname,
                is_overdue=is_overdue,
                days_until_due=days_until_due,
            )
            reminder_responses.append(reminder_response)

        return reminder_responses

    def _calculate_next_due_date(self, cron_expression: str) -> datetime:
        """Calculate the next due date from a cron expression."""
        # This is a simplified implementation
        # In a real app, you'd use a library like croniter

        # For now, just add a week for recurring reminders
        return datetime.utcnow() + timedelta(weeks=1)
