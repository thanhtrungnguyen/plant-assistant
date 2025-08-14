"""Organized Pydantic schemas for the plants module.

This module organizes schemas into logical groups for better maintainability.
All schemas are re-exported from this __init__.py for backward compatibility.
"""

# Plant schemas
# Care advice schemas
from .care import (
    CareRequest,
    CareResponse,
)

# Chat schemas
from .chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
)

# Dashboard schemas
from .dashboard import (
    DashboardResponse,
    DashboardStats,
)

# Diagnosis schemas
from .diagnosis import (
    DiagnoseRequest,
    DiagnoseResponse,
    PlantIssue,
    Remedy,
)

# Identification schemas
from .identification import (
    IdentifyRequest,
    IdentifyResponse,
    PlantIdentification,
)

# Pagination and list schemas
from .pagination import (
    PlantListParams,
    PlantListResponse,
    ReminderListParams,
    ReminderListResponse,
)

# Photo schemas
from .photos import (
    PlantPhotoBase,
    PlantPhotoCreate,
    PlantPhotoInDB,
    PlantPhotoResponse,
)
from .plants import (
    PlantBase,
    PlantCreate,
    PlantInDB,
    PlantResponse,
    PlantUpdate,
)

# Reminder schemas
from .reminders import (
    ReminderBase,
    ReminderCreate,
    ReminderInDB,
    ReminderResponse,
    ReminderUpdate,
)

# Species schemas
from .species import (
    SpeciesBase,
    SpeciesCreate,
    SpeciesInDB,
    SpeciesResponse,
)

# Re-export all schemas for backward compatibility
__all__ = [
    # Plant schemas
    "PlantBase",
    "PlantCreate",
    "PlantInDB",
    "PlantResponse",
    "PlantUpdate",
    # Species schemas
    "SpeciesBase",
    "SpeciesCreate",
    "SpeciesInDB",
    "SpeciesResponse",
    # Identification schemas
    "IdentifyRequest",
    "IdentifyResponse",
    "PlantIdentification",
    # Reminder schemas
    "ReminderBase",
    "ReminderCreate",
    "ReminderInDB",
    "ReminderResponse",
    "ReminderUpdate",
    # Photo schemas
    "PlantPhotoBase",
    "PlantPhotoCreate",
    "PlantPhotoInDB",
    "PlantPhotoResponse",
    # Pagination and list schemas
    "PlantListParams",
    "PlantListResponse",
    "ReminderListParams",
    "ReminderListResponse",
    # Care advice schemas
    "CareRequest",
    "CareResponse",
    # Diagnosis schemas
    "DiagnoseRequest",
    "DiagnoseResponse",
    "PlantIssue",
    "Remedy",
    # Dashboard schemas
    "DashboardResponse",
    "DashboardStats",
    # Chat schemas
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
]
