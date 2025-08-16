from pydantic import BaseModel
from typing import List, Dict, Optional


class LocationData(BaseModel):
    latitude: float
    longitude: float


class GeneratePodcastRequest(BaseModel):
    """Request model for generating podcast."""

    location: Optional[LocationData] = None


class GeneratePodcastInput(BaseModel):
    user_id: int  # Change to int to match database user IDs
    location: Optional[LocationData] = None


class UserData(BaseModel):
    address: str
    userName: str
    plants: str


class PodcastUserContext(BaseModel):
    """Structured user context specifically for podcast generation."""

    user_id: int
    plants_owned: List[str]
    common_care_issues: List[str]
    recent_recommendations: List[str]
    care_preferences: List[str]
    experience_level: str
    recent_diagnoses: List[Dict[str, str]]
    context_confidence: float
    last_updated: str
