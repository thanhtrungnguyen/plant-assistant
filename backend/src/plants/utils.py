"""Utility functions for plants module."""

import os
import uuid
from datetime import datetime
from typing import Dict, Any
import requests

from src.plants.constants import (
    MAX_PHOTO_SIZE_MB,
    ALLOWED_PHOTO_FORMATS,
    MIN_CONFIDENCE_THRESHOLD,
)
from src.plants.exceptions import InvalidPhotoFormatError, PhotoTooLargeError


def validate_photo_file(file_path: str, file_size: int) -> bool:
    """Validate photo file format and size."""
    # Check file size
    if file_size > MAX_PHOTO_SIZE_MB * 1024 * 1024:
        raise PhotoTooLargeError()

    # Check file extension
    file_ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    if file_ext not in ALLOWED_PHOTO_FORMATS:
        raise InvalidPhotoFormatError()

    return True


def generate_photo_filename(original_filename: str, plant_id: int) -> str:
    """Generate a unique filename for photo storage."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    file_ext = os.path.splitext(original_filename)[1].lower()

    return f"plant_{plant_id}_{timestamp}_{unique_id}{file_ext}"


def extract_photo_metadata(image_url: str) -> Dict[str, Any]:
    """Extract metadata from photo for AI analysis."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        # For now, return basic metadata
        # In a real implementation, this would include:
        # - Image dimensions
        # - EXIF data
        # - Color analysis
        # - Plant detection confidence

        metadata = {
            "file_size": len(response.content),
            "content_type": response.headers.get("content-type"),
            "extracted_at": datetime.utcnow().isoformat(),
        }

        return metadata

    except Exception as e:
        return {
            "error": str(e),
            "extracted_at": datetime.utcnow().isoformat(),
        }


def calculate_care_schedule(plant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate optimal care schedule based on plant data."""
    # This would integrate with species care requirements
    # For now, return a basic schedule

    base_schedule = {
        "watering": {"frequency_days": 7, "next_due": None, "last_completed": None},
        "fertilizing": {"frequency_days": 30, "next_due": None, "last_completed": None},
    }

    # Adjust based on plant characteristics
    if plant_data.get("light_conditions") == "low_light":
        base_schedule["watering"]["frequency_days"] = 10

    if plant_data.get("soil_type") == "cactus_mix":
        base_schedule["watering"]["frequency_days"] = 14

    return base_schedule


def analyze_plant_health_from_photos(photos: list) -> Dict[str, Any]:
    """Analyze plant health from recent photos."""
    if not photos:
        return {
            "health_score": None,
            "analysis": "No photos available for analysis",
            "confidence": 0.0,
        }

    # Mock analysis - in real implementation this would use AI vision
    health_analysis = {
        "health_score": 85,
        "analysis": "Plant appears healthy with good leaf color",
        "confidence": 0.82,
        "recommendations": ["Continue current care routine", "Monitor for new growth"],
        "warning_signs": [],
        "analyzed_photos": len(photos),
        "latest_photo_date": photos[0].created_at.isoformat() if photos else None,
    }

    return health_analysis


def generate_plant_insights(
    plant_data: Dict[str, Any], photos: list | None = None
) -> Dict[str, Any]:
    """Generate comprehensive AI insights for a plant."""
    insights = {
        "timestamp": datetime.utcnow().isoformat(),
        "plant_id": plant_data.get("id"),
        "insights": [],
    }

    # Care schedule insights
    care_schedule = calculate_care_schedule(plant_data)
    insights["insights"].append(
        {"type": "care_schedule", "data": care_schedule, "confidence": 0.9}
    )

    # Health analysis from photos
    if photos:
        health_analysis = analyze_plant_health_from_photos(photos)
        if health_analysis["confidence"] >= MIN_CONFIDENCE_THRESHOLD:
            insights["insights"].append(
                {
                    "type": "health_analysis",
                    "data": health_analysis,
                    "confidence": health_analysis["confidence"],
                }
            )

    # Growth predictions (mock)
    insights["insights"].append(
        {
            "type": "growth_prediction",
            "data": {
                "expected_growth": "moderate",
                "next_milestone": "new leaf development",
                "timeframe_days": 14,
            },
            "confidence": 0.7,
        }
    )

    return insights


def format_plant_summary(plant_data: Dict[str, Any]) -> str:
    """Format a human-readable plant summary."""
    summary_parts = []

    if plant_data.get("nickname"):
        summary_parts.append(f"Name: {plant_data['nickname']}")

    if plant_data.get("species_name"):
        summary_parts.append(f"Species: {plant_data['species_name']}")

    if plant_data.get("location_text"):
        summary_parts.append(f"Location: {plant_data['location_text']}")

    if plant_data.get("acquisition_date"):
        days_owned = (datetime.utcnow() - plant_data["acquisition_date"]).days
        summary_parts.append(f"Owned for: {days_owned} days")

    return " | ".join(summary_parts) if summary_parts else "Plant summary not available"
