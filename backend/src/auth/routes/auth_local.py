from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from anyio import to_thread
from datetime import datetime, timedelta, timezone

from src.auth.schemas import LoginIn, RegisterIn
from src.auth.services.auth_service import login_email_password, register_email_password
from src.core.config import settings
from src.core.logging import get_logger
from src.core.security import issue_tokens, set_auth_cookies
from src.database.session import get_db
from src.auth.repositories.auth_repo import store_refresh

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth-local"])


@router.post("/register")
async def register(
    payload: RegisterIn, response: Response, db: Session = Depends(get_db)
):
    logger.info(f"Registration attempt for email: {payload.email}")
    try:
        user = await to_thread.run_sync(
            register_email_password, db, payload.email, payload.password, payload.name
        )
        logger.info(f"User registered successfully with ID: {user.id}")
    except ValueError as e:
        logger.warning(f"Registration failed for {payload.email}: {str(e)}")
        raise HTTPException(409, str(e))

    access, refresh, jti = issue_tokens(sub=str(user.id))
    logger.info(f"Tokens issued for user {user.id}")
    # Store the refresh token in the database
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_DAYS)
    store_refresh(db, jti, user.id, expires_at)
    set_auth_cookies(response, access, refresh)
    logger.info(f"Auth cookies set for user {user.id}")
    return {"ok": True}


@router.post("/login")
async def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for email: {payload.email}")
    user = await to_thread.run_sync(
        login_email_password, db, payload.email, payload.password
    )
    if not user:
        logger.warning(f"Login failed for {payload.email}: Invalid credentials")
        raise HTTPException(401, "Invalid credentials")

    logger.info(f"User {user.id} logged in successfully")
    access, refresh, jti = issue_tokens(sub=str(user.id))
    logger.info(f"Tokens issued for user {user.id}")
    # Store the refresh token in the database
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_DAYS)
    store_refresh(db, jti, user.id, expires_at)
    set_auth_cookies(response, access, refresh)
    logger.info(f"Auth cookies set for user {user.id}")
    return {"ok": True}
