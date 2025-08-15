"""Plant identification-related Pydantic schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from src.identification.constants import (
    MAX_DESCRIPTION_LENGTH,
    MAX_IMAGES_PER_REQUEST,
    MIN_DESCRIPTION_LENGTH,
    IdentificationConfidence,
)


class IdentifyRequest(BaseModel):
    """Schema for plant identification request."""

    images: List[str] = Field(
        default_factory=list,
        description="Base64-encoded images",
        max_length=MAX_IMAGES_PER_REQUEST,
    )
    description: Optional[str] = Field(
        None,
        min_length=MIN_DESCRIPTION_LENGTH,
        max_length=MAX_DESCRIPTION_LENGTH,
        description="Text description of the plant",
    )
    user_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional context like location, conditions"
    )

    @model_validator(mode="after")
    def validate_input(self):
        """Ensure at least one input method is provided."""
        if not self.images and not self.description:
            raise ValueError("Either images or description must be provided")
        return self


class PlantIdentification(BaseModel):
    """Schema for a single plant identification result."""

    common_name: str
    scientific_name: str
    family: Optional[str] = None
    genus: Optional[str] = None
    native_origin: Optional[str] = None
    key_traits: List[str] = []
    growth_habits: Optional[str] = None
    confidence: float = Field(ge=0, le=1)


class IdentifyResponse(BaseModel):
    """Schema for plant identification response."""

    primary_identification: PlantIdentification
    alternatives: List[PlantIdentification] = Field(default_factory=list)
    fun_facts: List[str] = []
    basic_info: str
    disclaimer: str
    processing_time_ms: int
    confidence_level: IdentificationConfidence
