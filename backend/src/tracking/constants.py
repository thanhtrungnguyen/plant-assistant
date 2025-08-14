"""Constants for plant tracking module."""

# Growth stages
GROWTH_STAGES = [
    "seedling",
    "vegetative",
    "flowering",
    "fruiting",
    "mature",
    "dormant",
]

# Health indicators to track
HEALTH_INDICATORS = {
    "leaf_color": ["vibrant", "pale", "yellowing", "browning"],
    "leaf_texture": ["smooth", "rough", "wilted", "crispy"],
    "stem_condition": ["strong", "weak", "flexible", "brittle"],
    "growth_pattern": ["upright", "drooping", "spreading", "compact"],
    "root_health": ["white", "brown", "mushy", "dry"],
}

# Progress analysis categories
PROGRESS_CATEGORIES = [
    "growth",
    "health",
    "care",
    "environment",
    "flowering",
    "fruiting",
]

# Analysis thresholds
ANALYSIS_THRESHOLDS = {
    "min_photos_for_analysis": 2,
    "min_time_between_photos_hours": 24,
    "confidence_threshold": 0.7,
    "significant_health_change": 0.2,
    "significant_growth_change": 0.15,
}

# OpenAI model configuration
TRACKING_MODEL = "gpt-4o"
TRACKING_TEMPERATURE = 0.2
TRACKING_MAX_TOKENS = 1000

# Photo processing limits
MAX_PHOTO_SIZE = 1024  # pixels
SUPPORTED_FORMATS = ["JPEG", "PNG", "WebP"]
COMPRESSION_QUALITY = 90

# Timeline configuration
TIMELINE_GROUPING_DAYS = 7  # Group photos by week
MAX_TIMELINE_ENTRIES = 20
MAX_MILESTONES = 5

# Recommendation priorities
RECOMMENDATION_PRIORITIES = {
    "critical": 1,
    "important": 2,
    "suggested": 3,
}

# Default photo storage path pattern
PHOTO_URL_PATTERN = (
    "https://storage.example.com/plants/{plant_id}/photos/{photo_id}.jpg"
)

# Progress metrics defaults
DEFAULT_HEALTH_SCORE = 0.7
DEFAULT_GROWTH_RATE = "moderate"
DEFAULT_CONFIDENCE = 0.6
