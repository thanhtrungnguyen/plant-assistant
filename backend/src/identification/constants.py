"""Constants for plant identification module."""

from enum import Enum

# Request validation constants
MAX_IMAGES_PER_REQUEST = 5
MAX_DESCRIPTION_LENGTH = 750
MIN_DESCRIPTION_LENGTH = 10

# File size limits
MAX_FILE_SIZE_MB = 10
MAX_TOTAL_SIZE_MB = 10

# Supported image formats
SUPPORTED_IMAGE_FORMATS = ["JPEG", "PNG", "HEIC", "WEBP"]

# OpenAI settings
OPENAI_MODEL = "gpt-4o"
OPENAI_TEMPERATURE = 0.2

# Pinecone settings
PINECONE_TOP_K = 7
PINECONE_MIN_DISTANCE = 0.2

# Response settings
MIN_CONFIDENCE_THRESHOLD = 0.7
ALTERNATIVES_THRESHOLD = 0.85
MAX_ALTERNATIVES = 7


class IdentificationConfidence(Enum):
    """Confidence levels for plant identification."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
