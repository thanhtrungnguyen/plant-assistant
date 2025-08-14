"""Pydantic schemas for plants module."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from src.plants.constants import PlantStatus


class PlantBase(BaseModel):
    """Base schema for plant data."""

    nickname: Optional[str] = Field(None, description="User-given name for the plant")
    location_text: Optional[str] = Field(None, description="Where the plant is located")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="GPS latitude")
    longitude: Optional[float] = Field(
        None, ge=-180, le=180, description="GPS longitude"
    )
    light_conditions: Optional[str] = Field(
        None, description="Light exposure description"
    )
    soil_type: Optional[str] = Field(None, description="Type of soil being used")
    notes: Optional[str] = Field(None, description="Free-form notes about the plant")
    custom_attributes: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Custom user attributes"
    )


class PlantCreate(PlantBase):
    """Schema for creating a new plant."""

    species_id: Optional[int] = Field(None, description="ID of the plant species")
    acquisition_date: Optional[datetime] = Field(
        None, description="When the plant was acquired"
    )


class PlantUpdate(PlantBase):
    """Schema for updating a plant."""

    species_id: Optional[int] = Field(None, description="ID of the plant species")
    is_archived: Optional[bool] = Field(None, description="Whether plant is archived")


class PlantResponse(PlantBase):
    """Schema for plant response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    species_id: Optional[int] = None
    acquisition_date: Optional[datetime] = None
    is_archived: bool = False
    ai_metrics_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class PlantListParams(BaseModel):
    """Parameters for listing plants."""

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(None, description="Search term for plant names")
    status: Optional[PlantStatus] = Field(None, description="Filter by plant status")
    archived: Optional[bool] = Field(None, description="Filter by archived status")
    species_id: Optional[int] = Field(None, description="Filter by species")


class PlantListResponse(BaseModel):
    """Response schema for plant list."""

    plants: List[PlantResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PlantPhotoCreate(BaseModel):
    """Schema for creating a plant photo."""

    url: str = Field(..., description="URL of the uploaded photo")
    taken_at: Optional[datetime] = Field(None, description="When the photo was taken")
    caption: Optional[str] = Field(None, description="Caption for the photo")
    ai_metrics_json: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="AI analysis metadata"
    )


class PlantPhotoResponse(BaseModel):
    """Schema for plant photo response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    plant_id: int
    url: str
    taken_at: Optional[datetime] = None
    caption: Optional[str] = None
    ai_metrics_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class PlantShareCreate(BaseModel):
    """Schema for creating a plant share."""

    user_id: int = Field(..., description="ID of user to share with")
    role: str = Field(..., description="Role: viewer or editor")


class PlantShareResponse(BaseModel):
    """Schema for plant share response."""

    model_config = ConfigDict(from_attributes=True)

    plant_id: int
    user_id: int
    role: str
    created_at: datetime


class PlantInsightResponse(BaseModel):
    """Schema for AI-generated plant insights."""

    insight_type: str = Field(..., description="Type of insight: growth, health, etc.")
    message: str = Field(..., description="Human-readable insight message")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    data: Optional[Dict[str, Any]] = Field(None, description="Supporting data")
    generated_at: datetime
