"""Constants for the plants module."""

from enum import Enum


class PlantStatus(str, Enum):
    """Status of a plant."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ReminderType(str, Enum):
    """Types of plant care reminders."""

    WATERING = "watering"
    FERTILIZING = "fertilizing"
    PRUNING = "pruning"
    REPOTTING = "repotting"
    PEST_CHECK = "pest_check"
    CUSTOM = "custom"


class ReminderPriority(str, Enum):
    """Priority levels for reminders."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IdentificationConfidence(str, Enum):
    """Confidence levels for plant identification."""

    VERY_LOW = "very_low"  # 0-25%
    LOW = "low"  # 26-50%
    MEDIUM = "medium"  # 51-75%
    HIGH = "high"  # 76-90%
    VERY_HIGH = "very_high"  # 91-100%


class ErrorCode(str, Enum):
    """Error codes for the plants module."""

    PLANT_NOT_FOUND = "PLANT_NOT_FOUND"
    PLANT_ACCESS_DENIED = "PLANT_ACCESS_DENIED"
    INVALID_IMAGE_FORMAT = "INVALID_IMAGE_FORMAT"
    IMAGE_TOO_LARGE = "IMAGE_TOO_LARGE"
    TOO_MANY_IMAGES = "TOO_MANY_IMAGES"
    IDENTIFICATION_FAILED = "IDENTIFICATION_FAILED"
    REMINDER_NOT_FOUND = "REMINDER_NOT_FOUND"
    SPECIES_NOT_FOUND = "SPECIES_NOT_FOUND"


# Image processing constants
MAX_IMAGES_PER_REQUEST = 5
MAX_IMAGE_SIZE_MB = 2  # Per image
MAX_TOTAL_SIZE_MB = 10  # Total for all images
SUPPORTED_IMAGE_FORMATS = {"jpeg", "jpg", "png", "heic", "webp"}

# Text input limits
MAX_DESCRIPTION_LENGTH = 750
MIN_DESCRIPTION_LENGTH = 10

# Identification constants
MIN_CONFIDENCE_THRESHOLD = 0.25  # 25%
ALTERNATIVES_MIN_SIMILARITY = 0.8  # Cosine similarity threshold
MAX_ALTERNATIVES = 7

# Performance targets
API_RESPONSE_TARGET_MS = 1800  # 1.8 seconds
DASHBOARD_LOAD_TARGET_MS = 1000  # 1 second for 50 plants

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
