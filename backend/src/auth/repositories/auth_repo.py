from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.auth.models import RefreshToken


def store_refresh(db: Session, jti: str, user_id: int, expires_at: datetime):
    db.add(RefreshToken(jti=jti, user_id=user_id, expires_at=expires_at))
    db.commit()


def revoke_refresh(db: Session, jti: str):
    rt = db.get(RefreshToken, jti)
    if rt and not rt.revoked_at:
        rt.revoked_at = datetime.now(timezone.utc)
        db.commit()


def is_refresh_active(db: Session, jti: str) -> bool:
    rt = db.get(RefreshToken, jti)
    return bool(rt and not rt.revoked_at and rt.expires_at > datetime.now(timezone.utc))


def revoke_all_user_refresh_tokens(db: Session, user_id: int) -> int:
    now = datetime.now(timezone.utc)
    updated = (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .update({RefreshToken.revoked_at: now}, synchronize_session=False)
    )
    db.commit()
    return updated
