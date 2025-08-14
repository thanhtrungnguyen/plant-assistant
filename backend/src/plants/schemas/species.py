"""Species-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SpeciesBase(BaseModel):
    """Base schema for species data."""

    common_name: str = Field(max_length=200)
    scientific_name: str = Field(max_length=200)
    family: Optional[str] = Field(None, max_length=100)
    genus: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    care_instructions: Optional[Dict[str, Any]] = None


class SpeciesCreate(SpeciesBase):
    """Schema for creating a new species."""

    pass


class SpeciesInDB(SpeciesBase):
    """Schema for species data from database."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SpeciesResponse(SpeciesInDB):
    """Schema for species response."""

    plant_count: int = 0  # Number of plants of this species
