"""Tracking-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TrackPhotoUploadRequest(BaseModel):
    """Schema for uploading a tracking photo."""

    plant_id: UUID
    description: Optional[str] = Field(None, max_length=500)
    photo_data: str = Field(..., description="Base64 encoded image data")


class TrackPhotoResponse(BaseModel):
    """Schema for tracking photo response."""

    id: int
    plant_id: UUID
    url: str
    taken_at: datetime
    caption: Optional[str] = None
    ai_metrics_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class ProgressInsight(BaseModel):
    """Schema for a single progress insight."""

    type: str = Field(description="Type of insight (growth, health, care)")
    message: str = Field(description="Human-readable insight message")
    confidence: float = Field(ge=0, le=1, description="Confidence score")
    data: Optional[Dict[str, Any]] = None


class ProgressMetrics(BaseModel):
    """Schema for quantified progress metrics."""

    height_change: Optional[str] = None
    leaf_color_improvement: Optional[str] = None
    new_growth_detected: Optional[bool] = None
    overall_health_score: Optional[float] = Field(None, ge=0, le=1)
    growth_rate: Optional[str] = None


class ProgressRecommendation(BaseModel):
    """Schema for care recommendations based on progress."""

    title: str
    description: str
    priority: int = Field(ge=1, le=3, description="1=high, 2=medium, 3=low")
    category: str = Field(description="care, environment, growth, etc.")


class ProgressAnalysisRequest(BaseModel):
    """Schema for requesting progress analysis."""

    plant_id: UUID
    analysis_period_days: Optional[int] = Field(30, ge=7, le=365)
    include_recommendations: bool = True


class ProgressAnalysisResponse(BaseModel):
    """Schema for progress analysis response."""

    plant_id: UUID
    analysis_period_days: int
    total_photos: int
    insights: List[ProgressInsight]
    metrics: ProgressMetrics
    recommendations: List[ProgressRecommendation]
    analysis_date: datetime
    disclaimer: str


class ComparisonPhotoAnalysis(BaseModel):
    """Schema for comparing two photos."""

    before_photo_id: int
    after_photo_id: int
    comparison_insights: List[str]
    metrics_comparison: Dict[str, Any]
    confidence_score: float = Field(ge=0, le=1)


class GrowthTimelineEntry(BaseModel):
    """Schema for growth timeline entry."""

    date: datetime
    photo_count: int
    key_changes: List[str]
    health_score: Optional[float] = Field(None, ge=0, le=1)
    growth_stage: Optional[str] = None


class GrowthTimelineResponse(BaseModel):
    """Schema for growth timeline response."""

    plant_id: UUID
    timeline: List[GrowthTimelineEntry]
    overall_trend: str = Field(description="improving, stable, declining")
    key_milestones: List[str]
    generated_at: datetime
