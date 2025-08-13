from authlib.integrations.starlette_client import OAuth

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# Initialize OAuth
oauth = OAuth()

# Log OAuth initialization
logger.info("[AUTH] Initializing OAuth providers...")

# Conditionally configure Google OAuth
client_id = settings.GOOGLE_CLIENT_ID
client_secret = settings.GOOGLE_CLIENT_SECRET

if client_id and client_secret:
    # Mask sensitive information for logging
    masked_client_id = (
        f"{client_id[:8]}...{client_id[-4:]}" if len(client_id) > 12 else "****"
    )
    masked_client_secret = (
        f"{client_secret[:8]}...{client_secret[-4:]}"
        if len(client_secret) > 12
        else "****"
    )

    logger.info("[AUTH] Google OAuth configuration detected:")
    logger.info(f"   Client ID: {masked_client_id}")
    logger.info(f"   Client Secret: {masked_client_secret}")
    logger.info(
        "   Metadata URL: https://accounts.google.com/.well-known/openid-configuration"
    )
    logger.info("   Scopes: openid email profile")

    # Register Google OAuth provider
    try:
        oauth.register(
            name="google",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )
        logger.info("[AUTH] Google OAuth provider registered successfully")
    except Exception as e:
        logger.error(f"[AUTH] Failed to register Google OAuth provider: {e}")
else:
    if not client_id and not client_secret:
        logger.warning(
            "[AUTH] Google OAuth not configured: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are missing. Skipping provider registration."
        )
    elif not client_id:
        logger.warning(
            "[AUTH] Google OAuth not fully configured: GOOGLE_CLIENT_ID is missing. Skipping provider registration."
        )
    else:
        logger.warning(
            "[AUTH] Google OAuth not fully configured: GOOGLE_CLIENT_SECRET is missing. Skipping provider registration."
        )

logger.info("[AUTH] OAuth providers initialization completed")
