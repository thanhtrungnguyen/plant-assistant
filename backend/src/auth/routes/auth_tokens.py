from fastapi import APIRouter, Request, Response, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from src.core.security import (
    decode_refresh,
    set_auth_cookies,
    clear_auth_cookies,
    issue_tokens,
    decode_access,
)
from src.database.session import get_db
from src.auth.repositories.auth_repo import (
    is_refresh_active,
    revoke_refresh,
    store_refresh,
)

router = APIRouter(prefix="/auth", tags=["auth-tokens"])


@router.post("/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    claims = decode_refresh(request)
    jti = claims.get("jti")
    sub = claims.get("sub")
    if not jti or not is_refresh_active(db, jti):
        raise HTTPException(401)
    revoke_refresh(db, jti)
    access, new_refresh, new_jti = issue_tokens(sub=sub)
    expires_at = datetime.now(timezone.utc) + timedelta(days=14)  # align with settings
    store_refresh(db, new_jti, int(sub), expires_at)
    set_auth_cookies(response, access, new_refresh)
    return {"ok": True}


@router.post("/logout")
def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    try:
        claims = decode_refresh(request)
        if claims.get("jti"):
            revoke_refresh(db, claims["jti"])
    except Exception:
        pass
    clear_auth_cookies(response)
    return {"ok": True}


@router.get("/me")
def me(request: Request):
    user = decode_access(request)
    return {"sub": user["sub"]}
