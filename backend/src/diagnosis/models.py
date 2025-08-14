from typing import List

from pydantic import BaseModel


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
