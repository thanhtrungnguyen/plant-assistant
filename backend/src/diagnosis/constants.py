"""Constants for plant diagnosis module."""

from typing import Dict, List

# Default diagnosis categories
DEFAULT_DIAGNOSIS_CATEGORIES = [
    "environmental",
    "pest",
    "disease",
    "nutritional",
    "structural",
]

# Common plant issues by category
COMMON_PLANT_ISSUES = {
    "environmental": [
        "Overwatering",
        "Underwatering",
        "Light stress",
        "Temperature shock",
        "Low humidity",
        "Poor air circulation",
        "Transplant shock",
    ],
    "pest": [
        "Spider mites",
        "Aphids",
        "Scale insects",
        "Thrips",
        "Mealybugs",
        "Fungus gnats",
        "Whiteflies",
    ],
    "disease": [
        "Root rot",
        "Powdery mildew",
        "Bacterial leaf spot",
        "Fungal infection",
        "Crown rot",
        "Leaf blight",
        "Anthracnose",
    ],
    "nutritional": [
        "Nitrogen deficiency",
        "Phosphorus deficiency",
        "Potassium deficiency",
        "Iron deficiency",
        "Magnesium deficiency",
        "Calcium deficiency",
        "Over-fertilization",
    ],
    "structural": [
        "Root bound",
        "Weak stems",
        "Poor branching",
        "Stunted growth",
        "Leaf drop",
        "Wilting",
        "Deformities",
    ],
}

# Severity level mappings
SEVERITY_LEVELS = {
    "mild": {
        "score": 1,
        "description": "Minor issue, easily treatable",
        "urgency": "Low",
    },
    "moderate": {
        "score": 2,
        "description": "Noticeable problem requiring attention",
        "urgency": "Medium",
    },
    "severe": {
        "score": 3,
        "description": "Serious issue needing immediate action",
        "urgency": "High",
    },
    "critical": {
        "score": 4,
        "description": "Plant in danger, urgent intervention required",
        "urgency": "Critical",
    },
}

# Prevention tips by category
PREVENTION_TIPS: Dict[str, List[str]] = {
    "environmental": [
        "Monitor soil moisture regularly with a moisture meter",
        "Maintain consistent watering schedule based on plant needs",
        "Ensure adequate drainage in all pots and containers",
        "Provide appropriate light levels for plant species",
        "Maintain stable temperature and humidity levels",
        "Ensure proper air circulation around plants",
    ],
    "pest": [
        "Inspect plants regularly for early pest detection",
        "Quarantine new plants for 2 weeks before introducing to collection",
        "Keep plants clean and remove dead or dying foliage promptly",
        "Maintain proper spacing between plants for air circulation",
        "Use beneficial insects as natural pest control",
        "Clean pruning tools between plants to prevent spread",
    ],
    "disease": [
        "Avoid overhead watering to prevent fungal issues",
        "Sterilize all tools and equipment between uses",
        "Remove infected plant material immediately",
        "Improve air circulation to reduce moisture buildup",
        "Use pathogen-free potting soil and clean containers",
        "Monitor plants closely after any stress events",
    ],
    "nutritional": [
        "Test soil regularly to monitor nutrient levels",
        "Follow fertilization schedule appropriate for plant type",
        "Use balanced fertilizers unless specific deficiencies identified",
        "Flush soil periodically to prevent salt buildup",
        "Adjust pH if necessary for optimal nutrient uptake",
        "Avoid over-fertilization which can cause nutrient burn",
    ],
    "structural": [
        "Repot plants when they become root-bound",
        "Provide adequate support for tall or heavy plants",
        "Prune regularly to maintain shape and health",
        "Monitor growth patterns and adjust care accordingly",
        "Ensure containers are appropriate size for plant maturity",
        "Train climbing plants with proper support structures",
    ],
    "general": [
        "Establish consistent care routines and monitor plant responses",
        "Keep detailed records of care activities and plant health",
        "Research specific needs of each plant species in your collection",
        "Address problems early before they become severe",
        "Maintain clean growing environment and tools",
        "Learn to recognize normal vs. abnormal plant behavior",
    ],
}

# OpenAI model configuration
DIAGNOSIS_MODEL = "gpt-4o"
DIAGNOSIS_TEMPERATURE = 0.3
DIAGNOSIS_MAX_TOKENS = 2000

# Vision analysis configuration
VISION_MODEL = "gpt-4o"
VISION_TEMPERATURE = 0.2
VISION_MAX_TOKENS = 1000

# Image processing limits
MAX_IMAGE_SIZE = 1024  # pixels
MAX_IMAGES_PER_REQUEST = 5
SUPPORTED_IMAGE_FORMATS = ["JPEG", "PNG", "WebP"]

# Confidence thresholds
MIN_CONFIDENCE_THRESHOLD = 0.3
HIGH_CONFIDENCE_THRESHOLD = 0.7
VERY_HIGH_CONFIDENCE_THRESHOLD = 0.9
