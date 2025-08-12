import jwt
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import Response, Request, HTTPException
from src.core.config import settings


def issue_tokens(sub: str):
    now = datetime.now(timezone.utc)
    access = jwt.encode(
        {"sub": sub, "exp": now + timedelta(minutes=settings.ACCESS_MIN)},
        settings.JWT_SECRET,  # type: ignore
        algorithm="HS256",
    )
    jti = str(uuid.uuid4())
    refresh = jwt.encode(
        {
            "sub": sub,
            "typ": "refresh",
            "jti": jti,
            "exp": now + timedelta(days=settings.REFRESH_DAYS),
        },
        settings.JWT_SECRET,  # type: ignore
        algorithm="HS256",
    )
    return access, refresh, jti


def set_auth_cookies(response: Response, access: str, refresh: str):
    common = dict(
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
    )
    response.set_cookie(
        "access_token",
        access,
        max_age=settings.ACCESS_MIN * 60,
        **common,  # type: ignore
    )
    response.set_cookie(
        "refresh_token",
        refresh,
        max_age=settings.REFRESH_DAYS * 24 * 3600,
        **common,  # type: ignore
    )


def clear_auth_cookies(response: Response):
    for name in ("access_token", "refresh_token", settings.CSRF_COOKIE_NAME):
        response.delete_cookie(name, domain=settings.COOKIE_DOMAIN)


def decode_access(request: Request):
    t = request.cookies.get("access_token")
    if not t:
        raise HTTPException(status_code=401)
    try:
        return jwt.decode(t, settings.JWT_SECRET, algorithms=["HS256"])  # type: ignore
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid")


def decode_refresh(request: Request):
    t = request.cookies.get("refresh_token")
    if not t:
        raise HTTPException(status_code=401)
    try:
        c = jwt.decode(t, settings.JWT_SECRET, algorithms=["HS256"])  # type: ignore
        if c.get("typ") != "refresh":
            raise HTTPException(status_code=401)
        return c
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401)


def set_csrf_cookie(response: Response, token: str):
    response.set_cookie(
        settings.CSRF_COOKIE_NAME,
        token,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,  # type: ignore
        domain=settings.COOKIE_DOMAIN,
        max_age=7 * 24 * 3600,
    )


def verify_csrf(request: Request):
    header = request.headers.get("x-csrf-token")
    cookie = request.cookies.get(settings.CSRF_COOKIE_NAME)
    if not header or not cookie or header != cookie:
        raise HTTPException(status_code=403, detail="CSRF check failed")
