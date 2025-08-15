"""Exceptions for plants module."""

from src.shared.exceptions import BaseAPIException


class PlantNotFoundError(BaseAPIException):
    """Plant not found."""

    status_code = 404
    message = "Plant not found"


class PlantAccessDeniedError(BaseAPIException):
    """User doesn't have access to the plant."""

    status_code = 403
    message = "Access denied to this plant"


class PlantPhotoNotFoundError(BaseAPIException):
    """Plant photo not found."""

    status_code = 404
    message = "Plant photo not found"


class InvalidPlantDataError(BaseAPIException):
    """Invalid plant data provided."""

    status_code = 400
    message = "Invalid plant data"


class PlantShareNotFoundError(BaseAPIException):
    """Plant share not found."""

    status_code = 404
    message = "Plant share not found"


class PhotoUploadError(BaseAPIException):
    """Error uploading photo."""

    status_code = 400
    message = "Error uploading photo"


class InvalidPhotoFormatError(BaseAPIException):
    """Invalid photo format."""

    status_code = 400
    message = "Invalid photo format. Allowed formats: jpg, jpeg, png, webp"


class PhotoTooLargeError(BaseAPIException):
    """Photo file too large."""

    status_code = 400
    message = "Photo file too large. Maximum size: 10MB"
