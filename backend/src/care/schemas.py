"""Care advice-related Pydantic schemas."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CareRequest(BaseModel):
    """Schema for plant care advice request."""

    plant_id: Optional[UUID] = None
    location: str = Field(description="ZIP code or location")
    environment: Dict[str, Any] = Field(description="Environment details")
    preferences: List[str] = Field(
        default_factory=list, description="User care preferences"
    )


class CareResponse(BaseModel):
    """Schema for plant care advice response."""

    plan: Dict[str, str] = Field(
        description="Care instructions by category (watering, light, soil, etc.)"
    )
    seasonal_adjustments: Dict[str, List[str]] = Field(
        description="Seasonal care modifications"
    )
    eco_tips: List[str] = Field(description="Environmentally friendly care suggestions")
    sources: List[str] = Field(description="Reference sources for recommendations")
    disclaimer: str = Field(description="Care advice disclaimer")
