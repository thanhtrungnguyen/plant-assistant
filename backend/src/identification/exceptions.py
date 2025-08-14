"""Custom exceptions for plant identification module."""

from fastapi import HTTPException


class IdentificationFailedException(HTTPException):
    """Exception raised when plant identification fails."""

    def __init__(self, detail: str = "Plant identification failed"):
        super().__init__(status_code=422, detail=detail)


class InvalidImageFormatException(HTTPException):
    """Exception raised when uploaded image format is not supported."""

    def __init__(self, detail: str = "Invalid image format"):
        super().__init__(status_code=400, detail=detail)


class InvalidImageException(HTTPException):
    """Exception raised when uploaded image is invalid."""

    def __init__(self, detail: str = "Invalid image format or size"):
        super().__init__(status_code=400, detail=detail)


class NoInputProvidedException(HTTPException):
    """Exception raised when no images or description provided."""

    def __init__(self, detail: str = "No images or description provided"):
        super().__init__(status_code=400, detail=detail)


class RateLimitExceededException(HTTPException):
    """Exception raised when API rate limit is exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail)
