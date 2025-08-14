"""
Startup utilities for application initialization and health checks.
"""

from src.auth.providers import oauth
from src.core.config import settings
from src.core.logging import get_logger
from src.database.pinecone import ensure_index, get_pinecone
from src.integrations.openai_api.openai_api import openai_health_check

logger = get_logger(__name__)


def check_database_connection():
    """Check database connection and log status"""
    try:
        from sqlalchemy import text

        from src.database.session import engine

        # Test connection with a simple query (synchronous)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("[DATABASE] Connection successful")
        logger.info(
            f"[DATABASE] URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}"
        )
    except Exception as e:
        logger.error(f"[DATABASE] Connection failed: {e}")


def check_oauth_status():
    """Check OAuth providers and log status"""
    try:
        google_client = (
            oauth.create_client("google")
            if hasattr(oauth, "_clients") and "google" in oauth._clients
            else None
        )
        if google_client:
            logger.info("[OAUTH] Google OAuth provider: CONFIGURED")
        else:
            logger.warning("[OAUTH] Google OAuth provider: NOT CONFIGURED")
    except Exception as e:
        logger.error(f"[OAUTH] OAuth check failed: {e}")


def log_application_settings():
    """Log important application settings"""
    logger.info(f"Frontend URL: {settings.FRONTEND_URL}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")
    logger.info(
        f"JWT Secret: {'CONFIGURED' if settings.JWT_SECRET != 'change-me' else 'WARNING - Using default (change in production)'}"
    )
    logger.info(f"Access token expiry: {settings.ACCESS_MIN} minutes")
    logger.info(f"Refresh token expiry: {settings.REFRESH_DAYS} days")


def run_startup_checks():
    """Run all startup checks and log application status"""
    logger.info(f"Starting {settings.APP_NAME} application")

    # Log application settings
    log_application_settings()

    # Run database connection check
    try:
        check_database_connection()
    except Exception as e:
        logger.error(f"[DATABASE] Failed to test connection: {e}")

    # Run OAuth status check
    check_oauth_status()

    logger.info("Startup checks completed")

    # Pinecone (vector DB) check logged after other components
    try:
        pc = get_pinecone()
        if pc:
            # Lazy ensure default index if configured
            created = ensure_index()
            if created:
                logger.info(f"[PINECONE] Client ready. Default index: {created}")
            else:
                logger.info("[PINECONE] Client ready. No default index configured.")
        else:
            logger.warning("[PINECONE] Not configured (skipping)")
    except Exception as e:
        logger.error(f"[PINECONE] Initialization failed: {e}")

    # OpenAI check
    try:
        if settings.OPENAI_API_KEY:
            if openai_health_check():
                logger.info("[OPENAI] Connectivity OK")
            else:
                logger.error("[OPENAI] Health check failed")
        else:
            logger.warning("[OPENAI] Not configured (missing OPENAI_API_KEY)")
    except Exception as e:  # pragma: no cover
        logger.error(f"[OPENAI] Initialization error: {e}")
