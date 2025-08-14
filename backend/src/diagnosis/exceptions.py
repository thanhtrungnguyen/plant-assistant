"""Custom exceptions for plant diagnosis module."""


class DiagnosisBaseException(Exception):
    """Base exception for diagnosis related errors."""

    pass


class DiagnosisGenerationException(DiagnosisBaseException):
    """Raised when diagnosis generation fails."""

    pass


class ImageProcessingException(DiagnosisBaseException):
    """Raised when image processing fails."""

    pass


class SymptomParsingException(DiagnosisBaseException):
    """Raised when symptom parsing fails."""

    pass


class PlantContextNotFoundException(DiagnosisBaseException):
    """Raised when plant context cannot be retrieved."""

    pass


class OpenAIVisionException(DiagnosisBaseException):
    """Raised when OpenAI Vision API fails."""

    pass


class VectorSearchException(DiagnosisBaseException):
    """Raised when vector similarity search fails."""

    pass
