"""Custom exceptions for the plants module."""

from fastapi import HTTPException, status

from .constants import ErrorCode


class PlantNotFoundException(HTTPException):
    """Raised when a plant is not found."""

    def __init__(self, plant_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.PLANT_NOT_FOUND,
                "message": f"Plant with ID {plant_id} not found",
                "plant_id": plant_id,
            },
        )


class PlantAccessDeniedException(HTTPException):
    """Raised when user doesn't have access to a plant."""

    def __init__(self, plant_id: int):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": ErrorCode.PLANT_ACCESS_DENIED,
                "message": f"Access denied to plant with ID {plant_id}",
                "plant_id": plant_id,
            },
        )


class InvalidImageFormatException(HTTPException):
    """Raised when an uploaded image has an invalid format."""

    def __init__(self, format_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": ErrorCode.INVALID_IMAGE_FORMAT,
                "message": f"Invalid image format: {format_name}. Supported formats: jpeg, png, heic, webp",
                "format": format_name,
            },
        )


class ImageTooLargeException(HTTPException):
    """Raised when an uploaded image is too large."""

    def __init__(self, size_mb: float, max_size_mb: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error_code": ErrorCode.IMAGE_TOO_LARGE,
                "message": f"Image size {size_mb:.1f}MB exceeds maximum {max_size_mb}MB",
                "size_mb": size_mb,
                "max_size_mb": max_size_mb,
            },
        )


class TooManyImagesException(HTTPException):
    """Raised when too many images are uploaded."""

    def __init__(self, count: int, max_count: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": ErrorCode.TOO_MANY_IMAGES,
                "message": f"Too many images: {count}. Maximum allowed: {max_count}",
                "count": count,
                "max_count": max_count,
            },
        )


class IdentificationFailedException(HTTPException):
    """Raised when plant identification fails."""

    def __init__(self, reason: str = "Unknown error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": ErrorCode.IDENTIFICATION_FAILED,
                "message": f"Plant identification failed: {reason}",
                "reason": reason,
            },
        )


class ReminderNotFoundException(HTTPException):
    """Raised when a reminder is not found."""

    def __init__(self, reminder_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.REMINDER_NOT_FOUND,
                "message": f"Reminder with ID {reminder_id} not found",
                "reminder_id": reminder_id,
            },
        )


class SpeciesNotFoundException(HTTPException):
    """Raised when a species is not found."""

    def __init__(self, species_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ErrorCode.SPECIES_NOT_FOUND,
                "message": f"Species with ID {species_id} not found",
                "species_id": species_id,
            },
        )
