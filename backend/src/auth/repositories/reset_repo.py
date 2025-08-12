from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from sqlalchemy.orm import Session

from src.auth.models import PasswordResetToken


def hash_token(plain: str) -> str:
    return sha256(plain.encode("utf-8")).hexdigest()


def create_reset_token(
    db: Session,
    *,
    user_id: int,
    plain_token: str,
    expires_at: datetime,
    requested_ip: str | None,
    user_agent: str | None,
) -> PasswordResetToken:
    prt = PasswordResetToken(
        user_id=user_id,
        token_hash=hash_token(plain_token),
        expires_at=expires_at,
        requested_ip=requested_ip,
        user_agent=user_agent,
    )
    db.add(prt)
    db.commit()
    db.refresh(prt)
    return prt


def get_valid_token(db: Session, *, plain_token: str) -> PasswordResetToken | None:
    h = hash_token(plain_token)
    now = datetime.now(timezone.utc)
    prt = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == h,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
        .one_or_none()
    )
    return prt


def mark_used(db: Session, prt: PasswordResetToken) -> None:
    prt.used_at = datetime.now(timezone.utc)
    db.commit()
