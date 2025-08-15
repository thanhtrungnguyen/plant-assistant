"""Shared exception classes."""

from fastapi import HTTPException


class BaseAPIException(HTTPException):
    """Base exception for API errors."""

    status_code: int = 500
    message: str = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.message
        super().__init__(status_code=self.status_code, detail=self.detail)
