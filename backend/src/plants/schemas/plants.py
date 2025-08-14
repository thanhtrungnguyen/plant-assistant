"""Plant-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from ..constants import PlantStatus


# Base schemas
class PlantBase(BaseModel):
    """Base schema for plant data."""

    nickname: Optional[str] = Field(None, max_length=100)
    location_text: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=1000)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class PlantCreate(PlantBase):
    """Schema for creating a new plant."""

    species_id: Optional[int] = None
    acquisition_date: Optional[datetime] = None


class PlantUpdate(PlantBase):
    """Schema for updating a plant."""

    species_id: Optional[int] = None
    is_archived: Optional[bool] = None


class PlantInDB(PlantBase):
    """Schema for plant data from database."""

    id: int
    user_id: int
    species_id: Optional[int]
    acquisition_date: Optional[datetime]
    is_archived: bool
    ai_metrics_json: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlantResponse(PlantInDB):
    """Schema for plant response with additional computed fields."""

    status: PlantStatus = PlantStatus.UNKNOWN
    photo_count: int = 0
    last_care_date: Optional[datetime] = None
    next_reminder_date: Optional[datetime] = None
