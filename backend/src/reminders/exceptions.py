"""Exceptions for reminders module."""

from src.shared.exceptions import BaseAPIException


class ReminderNotFoundException(BaseAPIException):
    """Reminder not found."""

    status_code = 404
    message = "Reminder not found"


class ReminderAccessDeniedError(BaseAPIException):
    """User doesn't have access to the reminder."""

    status_code = 403
    message = "Access denied to this reminder"


class InvalidReminderDataError(BaseAPIException):
    """Invalid reminder data provided."""

    status_code = 400
    message = "Invalid reminder data"


class ReminderAlreadyCompletedError(BaseAPIException):
    """Reminder is already completed."""

    status_code = 400
    message = "Reminder is already completed"


class InvalidReminderFrequencyError(BaseAPIException):
    """Invalid reminder frequency."""

    status_code = 400
    message = "Invalid reminder frequency"
