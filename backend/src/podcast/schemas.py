from typing import Optional
import uuid
from typing import List
from fastapi_users import schemas
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