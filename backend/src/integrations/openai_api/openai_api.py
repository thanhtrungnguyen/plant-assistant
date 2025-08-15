"""OpenAI API integration helpers.

Provides a lazily initialized OpenAI client and utility functions
for health checks and standardized generation parameters.
"""

from __future__ import annotations

from email.mime import base
from typing import Any, Dict, Optional

from openai import OpenAI, OpenAIError, api_key, base_url  # type: ignore
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

_client: OpenAI | None = None


def get_openai_client() -> OpenAI | None:
    """Return cached OpenAI client or None if not configured."""
    global _client
    if _client is not None:
        return _client
    if not settings.OPENAI_API_KEY:
        logger.warning("OpenAI not configured: missing OPENAI_API_KEY")
        return None
    _client = OpenAI(base_url=settings.OPENAI_BASE_URL, api_key=settings.OPENAI_API_KEY)
    return _client


def openai_health_check() -> bool:
    """Perform a lightweight health check.

    Uses models.list() to verify API key validity. Returns True if accessible.
    """
    client = get_openai_client()
    if client is None:
        return False
    try:
        client.models.list()  # simple permission & connectivity check
        return True
    except OpenAIError as e:  # pragma: no cover - network path
        logger.error(f"[OPENAI] Health check failed: {e}")
        return False
    except Exception as e:  # pragma: no cover
        logger.error(f"[OPENAI] Unexpected error: {e}")
        return False


def default_completion_params(model_override: Optional[str] = None) -> Dict[str, Any]:
    """Return default completion parameters based on settings."""
    return {
        "model": model_override or settings.OPENAI_MODEL,
        "max_tokens": settings.OPENAI_MAX_TOKENS,
        "temperature": settings.OPENAI_TEMPERATURE,
    }


__all__ = [
    "get_openai_client",
    "openai_health_check",
    "default_completion_params",
]
