"""Custom exceptions for plant tracking module."""


class TrackingBaseException(Exception):
    """Base exception for tracking related errors."""

    pass


class TrackingAnalysisException(TrackingBaseException):
    """Raised when tracking analysis fails."""

    pass


class PhotoProcessingException(TrackingBaseException):
    """Raised when photo processing fails."""

    pass


class ProgressCalculationException(TrackingBaseException):
    """Raised when progress calculation fails."""

    pass


class TimelineGenerationException(TrackingBaseException):
    """Raised when timeline generation fails."""

    pass


class PhotoStorageException(TrackingBaseException):
    """Raised when photo storage operations fail."""

    pass


class InsightGenerationException(TrackingBaseException):
    """Raised when insight generation fails."""

    pass
