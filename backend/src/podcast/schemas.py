from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class LocationData(BaseModel):
    latitude: float
    longitude: float
    accuracy: float
    altitude: Optional[float] = None
    altitudeAccuracy: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None
    timestamp: int


class GeneratePodcastInput(BaseModel):
    user_id: UUID
    location: LocationData


class UserData(BaseModel):
    address: str
    userName: str
    plants: str
