"""Photo-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PlantPhotoBase(BaseModel):
    """Base schema for plant photo data."""

    filename: str = Field(max_length=255)
    original_filename: Optional[str] = Field(None, max_length=255)
    file_size: int = Field(gt=0)
    content_type: str = Field(max_length=50)
    description: Optional[str] = Field(None, max_length=500)


class PlantPhotoCreate(PlantPhotoBase):
    """Schema for creating a new plant photo."""

    plant_id: int
    image_data: str = Field(description="Base64-encoded image data")


class PlantPhotoInDB(PlantPhotoBase):
    """Schema for plant photo data from database."""

    id: int
    plant_id: int
    user_id: int
    ai_analysis: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class PlantPhotoResponse(PlantPhotoInDB):
    """Schema for plant photo response."""

    url: str  # Pre-signed URL or CDN URL
    thumbnail_url: Optional[str] = None
