"""Reminder-related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.reminders.constants import ReminderPriority, ReminderType


class ReminderBase(BaseModel):
    """Base schema for reminder data."""

    title: str = Field(max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    reminder_type: ReminderType
    priority: ReminderPriority = ReminderPriority.MEDIUM
    cron_expression: Optional[str] = Field(
        None, description="Cron expression for recurring reminders"
    )
    next_due_date: datetime
    is_recurring: bool = False


class ReminderCreate(ReminderBase):
    """Schema for creating a new reminder."""

    plant_id: int


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder."""

    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    reminder_type: Optional[ReminderType] = None
    priority: Optional[ReminderPriority] = None
    cron_expression: Optional[str] = None
    next_due_date: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    is_completed: Optional[bool] = None


class ReminderInDB(ReminderBase):
    """Schema for reminder data from database."""

    id: int
    plant_id: int
    user_id: int
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReminderResponse(ReminderInDB):
    """Schema for reminder response."""

    plant_nickname: Optional[str] = None
    is_overdue: bool = False
    days_until_due: Optional[int] = None


class ReminderListParams(BaseModel):
    """Parameters for listing reminders."""

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    plant_id: Optional[int] = Field(None, description="Filter by plant")
    reminder_type: Optional[ReminderType] = Field(None, description="Filter by type")
    priority: Optional[ReminderPriority] = Field(None, description="Filter by priority")
    overdue_only: bool = Field(False, description="Show only overdue reminders")


class ReminderListResponse(BaseModel):
    """Response schema for reminder list."""

    reminders: list[ReminderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
