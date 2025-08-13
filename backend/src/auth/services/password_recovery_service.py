from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from src.core.config import settings
from src.integrations.email.sender import send_password_reset_email
from src.auth.repositories import reset_repo
from src.auth.repositories.auth_repo import revoke_all_user_refresh_tokens
from src.auth.repositories.user_repo import get_user_by_email, set_password

RESET_TOKEN_BYTES = 48  # ~64 url-safe chars


def request_password_reset(
    db: Session, email: str, *, ip: str | None, ua: str | None, bg: BackgroundTasks
) -> None:
    user = get_user_by_email(db, email.lower())
    # Always behave the same (no email enumeration)
    if not user:
        return

    plain = secrets.token_urlsafe(RESET_TOKEN_BYTES)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_MINUTES
    )
    reset_repo.create_reset_token(
        db,
        user_id=user.id,
        plain_token=plain,
        expires_at=expires_at,
        requested_ip=ip,
        user_agent=ua,
    )

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={plain}"
    bg.add_task(send_password_reset_email, user.email, reset_link)


def reset_password(db: Session, *, token: str, new_password: str) -> bool:
    prt = reset_repo.get_valid_token(db, plain_token=token)
    if not prt:
        return False

    # Update password (bcrypt)
    set_password(db, prt.user_id, bcrypt.hash(new_password))

    # Invalidate the token and revoke all refresh sessions
    reset_repo.mark_used(db, prt)
    revoke_all_user_refresh_tokens(db, prt.user_id)
    return True
