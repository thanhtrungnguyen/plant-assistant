"""Dashboard-related Pydantic schemas."""

from typing import List

from pydantic import BaseModel

from .photos import PlantPhotoResponse
from .plants import PlantResponse
from .reminders import ReminderResponse


class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""

    total_plants: int
    healthy_plants: int
    plants_needing_attention: int
    overdue_reminders: int
    reminders_today: int
    reminders_this_week: int


class DashboardResponse(BaseModel):
    """Schema for dashboard data."""

    stats: DashboardStats
    recent_plants: List[PlantResponse]
    upcoming_reminders: List[ReminderResponse]
    recent_photos: List[PlantPhotoResponse]
