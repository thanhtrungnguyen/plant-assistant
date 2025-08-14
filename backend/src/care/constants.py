"""Constants for plant care advice."""

from typing import Dict, List

# Default care instructions fallback
DEFAULT_CARE_INSTRUCTIONS = {
    "watering": "Water when top inch of soil is dry, typically every 5-7 days",
    "light": "Provide bright, indirect light for 4-6 hours daily",
    "soil": "Use well-draining potting mix with good aeration",
    "humidity": "Maintain 40-60% humidity for optimal growth",
    "temperature": "Keep between 65-75°F (18-24°C) for best results",
    "fertilizing": "Feed with balanced fertilizer every 4 weeks during growing season",
    "repotting": "Repot every 1-2 years or when plant becomes root-bound",
    "pruning": "Remove dead or yellowing leaves regularly, prune for shape as needed",
}

# Seasonal adjustments by climate type
SEASONAL_ADJUSTMENTS: Dict[str, Dict[str, List[str]]] = {
    "temperate": {
        "spring": [
            "Resume regular fertilizing as growth begins",
            "Gradually increase watering frequency",
            "Check for repotting needs",
            "Begin outdoor acclimation if desired",
        ],
        "summer": [
            "Monitor for increased water needs",
            "Provide shade during intense afternoon heat",
            "Increase humidity if using air conditioning",
            "Watch for pest activity",
        ],
        "fall": [
            "Gradually reduce fertilizing frequency",
            "Prepare plants for winter dormancy",
            "Reduce watering as growth slows",
            "Bring outdoor plants inside before frost",
        ],
        "winter": [
            "Reduce watering frequency by 25-30%",
            "Avoid fertilizing during dormant period",
            "Provide supplemental lighting if needed",
            "Protect from cold drafts and dry air",
        ],
    },
    "cold": {
        "spring": [
            "Start fertilizing later in season",
            "Watch for late frost damage",
            "Gradually increase light exposure",
        ],
        "summer": [
            "Take advantage of growing season",
            "Monitor for rapid growth spurts",
            "Ensure adequate drainage during rainy periods",
        ],
        "fall": [
            "Prepare early for winter dormancy",
            "Begin winter protection measures",
            "Harvest seeds if applicable",
        ],
        "winter": [
            "Provide supplemental heating if needed",
            "Drastically reduce watering",
            "Consider grow lights for longer dark periods",
            "Protect from freezing temperatures",
        ],
    },
    "warm": {
        "spring": [
            "Begin pest prevention measures",
            "Increase ventilation as temperatures rise",
            "Watch for early flowering",
        ],
        "summer": [
            "Provide extra shade and cooling",
            "Increase watering frequency significantly",
            "Monitor for heat stress",
            "Ensure excellent air circulation",
        ],
        "fall": [
            "Continue regular care routine",
            "Watch for second growth spurts",
            "Maintain pest vigilance",
        ],
        "winter": [
            "Reduce watering slightly but maintain consistency",
            "Provide protection from occasional cold snaps",
            "Continue light fertilizing for evergreen varieties",
        ],
    },
}

# Eco-friendly care tips
ECO_FRIENDLY_TIPS = [
    "Collect rainwater for watering to reduce chemical exposure and conserve resources",
    "Use organic compost instead of synthetic fertilizers for sustainable nutrition",
    "Companion plant with herbs like basil or mint to naturally deter pests",
    "Recycle containers and household items for propagation and repotting",
    "Create your own organic pest spray using neem oil and mild dish soap",
    "Use coffee grounds as natural fertilizer for acid-loving plants",
    "Implement beneficial insects like ladybugs for natural pest control",
    "Make DIY organic potting mix using compost, perlite, and coconut coir",
    "Use diluted banana peel water as natural potassium-rich fertilizer",
    "Practice crop rotation principles even for houseplants to prevent soil depletion",
]

# API response limits
MAX_CARE_PLAN_LENGTH = 2000
MAX_SEASONAL_TIPS_PER_SEASON = 5
MAX_ECO_TIPS = 10

# OpenAI model configuration
OPENAI_MODEL = "gpt-4o"
OPENAI_TEMPERATURE = 0.3
OPENAI_MAX_TOKENS = 1500

# Location processing patterns
ZIP_CODE_PATTERN = r"^\d{5}(-\d{4})?$"
USDA_ZONE_PATTERN = r"^(\d{1,2}[ab]?)$"

# Default fallback values
DEFAULT_HARDINESS_ZONE = "7a"
DEFAULT_CLIMATE_TYPE = "temperate"
DEFAULT_TEMP_RANGE = "60-75°F"
