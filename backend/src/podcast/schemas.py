from pydantic import BaseModel
from uuid import UUID


class LocationData(BaseModel):
    latitude: float
    longitude: float


class GeneratePodcastInput(BaseModel):
    user_id: UUID
    location: LocationData


class UserData(BaseModel):
    address: str
    userName: str
    plants: str
