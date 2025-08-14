"""Constants for reminders module."""

from enum import Enum


class ReminderType(str, Enum):
    """Types of plant reminders."""

    WATERING = "watering"
    FERTILIZING = "fertilizing"
    PRUNING = "pruning"
    REPOTTING = "repotting"
    PEST_CHECK = "pest_check"
    GENERAL_CARE = "general_care"


class ReminderPriority(str, Enum):
    """Priority levels for reminders."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ReminderStatus(str, Enum):
    """Reminder status options."""

    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


# Frequency options for recurring reminders
class ReminderFrequency(str, Enum):
    """Frequency options for recurring reminders."""

    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    CUSTOM = "custom"


# Default reminder schedules by care type (in days)
DEFAULT_REMINDER_SCHEDULES = {
    ReminderType.WATERING: 7,
    ReminderType.FERTILIZING: 30,
    ReminderType.PRUNING: 90,
    ReminderType.REPOTTING: 365,
    ReminderType.PEST_CHECK: 14,
    ReminderType.GENERAL_CARE: 30,
}

# Notification timing (hours before due)
NOTIFICATION_TIMING = {
    ReminderPriority.LOW: 24,
    ReminderPriority.MEDIUM: 12,
    ReminderPriority.HIGH: 6,
    ReminderPriority.URGENT: 2,
}
