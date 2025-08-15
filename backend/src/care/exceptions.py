"""Custom exceptions for plant care advice module."""


class CareAdviceBaseException(Exception):
    """Base exception for care advice related errors."""

    pass


class InvalidLocationException(CareAdviceBaseException):
    """Raised when provided location cannot be processed or validated."""

    pass


class CareAdviceGenerationException(CareAdviceBaseException):
    """Raised when care advice generation fails."""

    pass


class USDAZoneNotFoundException(CareAdviceBaseException):
    """Raised when USDA hardiness zone cannot be determined for location."""

    pass


class PlantDataNotFoundException(CareAdviceBaseException):
    """Raised when plant data cannot be retrieved from database."""

    pass


class OpenAIServiceException(CareAdviceBaseException):
    """Raised when OpenAI service is unavailable or returns errors."""

    pass
