"""Router for plant reminder endpoints."""

from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.auth.models import User
from src.database.session import get_db
from src.plants.constants import ReminderPriority, ReminderType
from src.plants.dependencies import get_current_user_from_request
from src.plants.schemas import (
    ReminderCreate,
    ReminderListParams,
    ReminderListResponse,
    ReminderResponse,
    ReminderUpdate,
)
from src.plants.services import ReminderService

router = APIRouter(prefix="/plants/reminders", tags=["plant-reminders"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Create a new reminder for a plant."""
    service = ReminderService(db)
    reminder = service.create_reminder(reminder_data, current_user)

    return ReminderResponse(
        **reminder.__dict__,
        plant_nickname=None,  # Would be populated in full implementation
        is_overdue=False,
        days_until_due=None,
    )


@router.get("/", response_model=ReminderListResponse)
async def get_reminders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    plant_id: int = Query(None),
    reminder_type: ReminderType = Query(None),
    priority: ReminderPriority = Query(None),
    is_completed: bool = Query(None),
    overdue_only: bool = Query(False),
    sort_by: str = Query("next_due_date"),
    sort_order: str = Query("asc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Get paginated list of user's reminders."""
    params = ReminderListParams(
        page=page,
        size=size,
        plant_id=plant_id,
        reminder_type=reminder_type,
        priority=priority,
        is_completed=is_completed,
        overdue_only=overdue_only,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    service = ReminderService(db)
    reminders, total = service.get_user_reminders(current_user, params)

    pages = (total + size - 1) // size

    return ReminderListResponse(
        reminders=reminders,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/upcoming", response_model=List[ReminderResponse])
async def get_upcoming_reminders(
    days_ahead: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Get upcoming reminders for the next N days."""
    service = ReminderService(db)
    reminders = service.get_upcoming_reminders(current_user, days_ahead)
    return reminders


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Get a specific reminder by ID."""
    service = ReminderService(db)
    reminder = service.get_reminder_by_id(reminder_id, current_user)

    return ReminderResponse(
        **reminder.__dict__,
        plant_nickname=None,
        is_overdue=False,
        days_until_due=None,
    )


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: int,
    reminder_data: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Update a reminder."""
    service = ReminderService(db)
    updated_reminder = service.update_reminder(reminder_id, reminder_data, current_user)

    return ReminderResponse(
        **updated_reminder.__dict__,
        plant_nickname=None,
        is_overdue=False,
        days_until_due=None,
    )


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_request),
):
    """Delete a reminder."""
    service = ReminderService(db)
    service.delete_reminder(reminder_id, current_user)
