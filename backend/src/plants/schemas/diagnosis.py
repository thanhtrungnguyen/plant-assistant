"""Diagnosis-related Pydantic schemas."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DiagnoseRequest(BaseModel):
    """Schema for plant diagnosis request."""

    symptoms: Optional[str] = Field(None, max_length=1000)
    images: List[str] = Field(default_factory=list, max_length=4)
    plant_id: Optional[UUID] = None


class PlantIssue(BaseModel):
    """Schema for a plant issue identification."""

    category: str = Field(
        description="Issue category (pest, disease, environmental, nutrient)"
    )
    name: str = Field(description="Specific issue name")
    severity: str = Field(description="mild, moderate, or severe")
    probability: float = Field(ge=0, le=1, description="Confidence score")
    root_cause: Optional[str] = None


class Remedy(BaseModel):
    """Schema for a treatment remedy."""

    title: str
    steps: List[str]
    timeline: str
    priority: int = Field(ge=1, le=3, description="1=high, 2=medium, 3=low")
    is_organic: bool = True


class DiagnoseResponse(BaseModel):
    """Schema for plant diagnosis response."""

    issues: List[PlantIssue]
    remedies: List[Remedy]
    prevention: List[str]
    similar_cases: int = Field(description="Number of similar cases found")
    severity: int = Field(ge=1, le=3, description="Overall severity rating")
    disclaimer: str
