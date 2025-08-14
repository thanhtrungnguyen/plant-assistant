import uuid
from typing import List

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


# Plant Diagnosis Schemas


class ActionStep(BaseModel):
    id: int
    action: str


class PlantDiagnosisResponse(BaseModel):
    plant_name: str
    condition: str
    detail_diagnosis: str
    action_plan: List[ActionStep]


class PlantDiagnosisError(BaseModel):
    error: str
    message: str
