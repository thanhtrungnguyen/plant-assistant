from fastapi import APIRouter, Request, Depends, HTTPException
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from anyio import to_thread
from datetime import datetime, timedelta, timezone
from src.auth.providers import oauth
from src.core.config import settings
from src.core.logging import get_logger
from src.core.security import issue_tokens, set_auth_cookies, decode_access
from src.database.session import get_db
from src.auth.services.oauth_service import signin_or_link_google
from src.auth.repositories.user_repo import get_oauth_by_sub, link_oauth
from src.auth.repositories.auth_repo import store_refresh

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth-oauth"])


@router.get("/login/google")
async def login_google(request: Request, mode: str | None = None):
    redirect_uri = request.url_for("callback_google")
    # Only add mode parameter if it's actually provided
    if mode:
        redirect_uri = f"{redirect_uri}?mode={mode}"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback/google", name="callback_google")
async def callback_google(
    request: Request,
    db: Session = Depends(get_db),
    mode: str | None = None,
):
    token = await oauth.google.authorize_access_token(request)
    info = token.get("userinfo") or {}
    sub = info.get("sub")
    email = (info.get("email") or "").lower()
    email_verified = bool(info.get("email_verified"))
    name = info.get("name")

    logger.info(f"[OAuth] Google callback - sub: {sub}, email: {email}, verified: {email_verified}, name: {name}")

    if not sub:
        logger.error("[OAuth] No provider subject from Google")
        raise HTTPException(400, "No provider subject")

    if mode == "link":
        try:
            claims = decode_access(request)
        except Exception:
            raise HTTPException(401, "Login required to link")
        current_user_id = int(claims["sub"])
        existing = await to_thread.run_sync(get_oauth_by_sub, db, "google", sub)
        if existing and existing.user_id != current_user_id:
            raise HTTPException(
                409, "This Google account is already linked to another user"
            )
        if not existing:
            await to_thread.run_sync(link_oauth, db, current_user_id, "google", sub, email or None)
        return RedirectResponse(url=f"{settings.WEB_APP_URL}/settings/connections")

    # Sign-in or create+link
    try:
        user = await to_thread.run_sync(signin_or_link_google, db, sub, email or None, email_verified, name)
    except ValueError as e:
        raise HTTPException(409, str(e))

    if user and not user.is_active:
        raise HTTPException(403, "Account disabled")

    if user:
        logger.info(f"[OAuth] User found: {user.id}, email: {user.email}")
        access, refresh, jti = issue_tokens(sub=str(user.id))
        logger.info(f"[OAuth] Tokens issued for user {user.id}")
        # Store the refresh token in the database
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_DAYS)
        store_refresh(db, jti, user.id, expires_at)
        logger.info(f"[OAuth] Refresh token stored for user {user.id}")

        # Create redirect response first, then set cookies on it
        redirect_url = f"{settings.WEB_APP_URL}/chatbot"
        logger.info(f"[OAuth] Redirecting to: {redirect_url}")
        redirect_response = RedirectResponse(url=redirect_url)

        # Set cookies on the redirect response
        set_auth_cookies(redirect_response, access, refresh)
        logger.info(f"[OAuth] Auth cookies set for user {user.id}")

        return redirect_response
    else:
        logger.error("[OAuth] Failed to create or find user")
        raise HTTPException(500, "Failed to create or find user")
