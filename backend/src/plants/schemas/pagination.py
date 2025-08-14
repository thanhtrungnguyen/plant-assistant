"""Pagination and list-related Pydantic schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from ..constants import PlantStatus, ReminderPriority, ReminderType
from .plants import PlantResponse
from .reminders import ReminderResponse


class PlantListParams(BaseModel):
    """Schema for plant list query parameters."""

    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    search: Optional[str] = Field(None, max_length=100)
    species_id: Optional[int] = None
    status: Optional[PlantStatus] = None
    is_archived: Optional[bool] = None
    sort_by: str = Field("created_at")
    sort_order: str = Field("desc")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        allowed = ["created_at", "updated_at", "nickname", "acquisition_date"]
        if v not in allowed:
            raise ValueError(f"sort_by must be one of: {allowed}")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v


class PlantListResponse(BaseModel):
    """Schema for paginated plant list response."""

    plants: List[PlantResponse]
    total: int
    page: int
    size: int
    pages: int


class ReminderListParams(BaseModel):
    """Schema for reminder list query parameters."""

    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    plant_id: Optional[int] = None
    reminder_type: Optional[ReminderType] = None
    priority: Optional[ReminderPriority] = None
    is_completed: Optional[bool] = None
    overdue_only: bool = False
    sort_by: str = Field("next_due_date")
    sort_order: str = Field("asc")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        allowed = ["next_due_date", "created_at", "priority"]
        if v not in allowed:
            raise ValueError(f"sort_by must be one of: {allowed}")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v


class ReminderListResponse(BaseModel):
    """Schema for paginated reminder list response."""

    reminders: List[ReminderResponse]
    total: int
    page: int
    size: int
    pages: int
