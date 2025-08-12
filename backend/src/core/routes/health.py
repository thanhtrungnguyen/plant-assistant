from __future__ import annotations

from fastapi import APIRouter, HTTPException
from src.core.config import settings
from src.core.logging import get_logger
from src.database.health import db_ready

logger = get_logger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
def healthz():
    logger.debug("Health check requested")
    return {
        "status": "ok",
        "service": getattr(settings, "APP_NAME", "api"),
    }


@router.get("/ready", summary="Readiness probe")
def readyz():
    logger.info("Readiness check requested")
    checks = {
        "db": db_ready(),
    }

    if not all(checks.values()):
        logger.warning(f"Readiness check failed: {checks}")
        # 503 so load balancers / K8s don't send traffic yet
        raise HTTPException(
            status_code=503, detail={"status": "degraded", "checks": checks}
        )

    logger.info("Readiness check passed")
    return {"status": "ok", "checks": checks}
