from typing import Optional
import uuid

from fastapi_users import schemas
from pydantic import BaseModel
from uuid import UUID


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    quantity: int | None = None


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: UUID
    user_id: UUID
    model_config = {"from_attributes": True}

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