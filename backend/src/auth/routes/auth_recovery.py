from __future__ import annotations

from fastapi import APIRouter, Depends, BackgroundTasks, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.auth.services.password_recovery_service import (
    request_password_reset,
    reset_password,
)

router = APIRouter(prefix="/auth/password", tags=["auth-recovery"])


class ForgotIn(BaseModel):
    email: EmailStr


@router.post("/forgot")
async def forgot_password(
    payload: ForgotIn,
    request: Request,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    # no CSRF required; no session yet
    request_password_reset(db, payload.email, ip=ip, ua=ua, bg=bg)
    # Always return 200 (avoid email enumeration)
    return {"ok": True}


class ResetIn(BaseModel):
    token: str
    password: str


@router.post("/reset")
async def reset_password_route(payload: ResetIn, db: Session = Depends(get_db)):
    ok = reset_password(db, token=payload.token, new_password=payload.password)
    # Always 200, with status indicator (no enumeration on invalid/expired)
    return {"ok": ok}
