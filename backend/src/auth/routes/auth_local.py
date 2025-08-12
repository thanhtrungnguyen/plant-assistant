from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from src.auth.schemas import LoginIn, RegisterIn
from src.auth.services.auth_service import login_email_password, register_email_password
from src.core.logging import get_logger
from src.core.security import issue_tokens, set_auth_cookies
from src.database.session import get_db

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth-local"])


@router.post("/register")
def register(payload: RegisterIn, response: Response, db: Session = Depends(get_db)):
    logger.info(f"Registration attempt for email: {payload.email}")
    try:
        user = register_email_password(
            db, payload.email, payload.password, payload.name
        )
        logger.info(f"User registered successfully with ID: {user.id}")
    except ValueError as e:
        logger.warning(f"Registration failed for {payload.email}: {str(e)}")
        raise HTTPException(409, str(e))

    access, refresh, jti = issue_tokens(sub=str(user.id))
    logger.info(f"Tokens issued for user {user.id}")
    # TODO: store_refresh(...)
    set_auth_cookies(response, access, refresh)
    logger.info(f"Auth cookies set for user {user.id}")
    return {"ok": True}


@router.post("/login")
def login(payload: LoginIn, response: Response, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for email: {payload.email}")
    user = login_email_password(db, payload.email, payload.password)
    if not user:
        logger.warning(f"Login failed for {payload.email}: Invalid credentials")
        raise HTTPException(401, "Invalid credentials")

    logger.info(f"User {user.id} logged in successfully")
    access, refresh, jti = issue_tokens(sub=str(user.id))
    logger.info(f"Tokens issued for user {user.id}")
    # TODO: store_refresh(...)
    set_auth_cookies(response, access, refresh)
    logger.info(f"Auth cookies set for user {user.id}")
    return {"ok": True}
