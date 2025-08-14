"""Constants for plants module."""

from enum import Enum


class PlantStatus(str, Enum):
    """Plant status options."""

    HEALTHY = "healthy"
    NEEDS_ATTENTION = "needs_attention"
    SICK = "sick"
    THRIVING = "thriving"
    DORMANT = "dormant"
    DEAD = "dead"


class CareDifficulty(str, Enum):
    """Plant care difficulty levels."""

    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"
    EXPERT = "expert"


class LightConditions(str, Enum):
    """Light condition options."""

    FULL_SUN = "full_sun"
    PARTIAL_SUN = "partial_sun"
    SHADE = "shade"
    INDIRECT_LIGHT = "indirect_light"
    LOW_LIGHT = "low_light"


class SoilType(str, Enum):
    """Soil type options."""

    POTTING_MIX = "potting_mix"
    GARDEN_SOIL = "garden_soil"
    SANDY = "sandy"
    CLAY = "clay"
    LOAMY = "loamy"
    CACTUS_MIX = "cactus_mix"
    ORCHID_BARK = "orchid_bark"


# Photo upload constants
MAX_PHOTO_SIZE_MB = 10
ALLOWED_PHOTO_FORMATS = {"jpg", "jpeg", "png", "webp"}

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# AI insights constants
MIN_CONFIDENCE_THRESHOLD = 0.5
MAX_INSIGHTS_PER_PLANT = 10
