from fastapi import APIRouter, Request, Response, Depends, HTTPException
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.auth.providers import oauth
from src.core.config import settings
from src.core.security import issue_tokens, set_auth_cookies, decode_access
from src.database.session import get_db
from src.auth.services.oauth_service import signin_or_link_google
from src.auth.repositories.user_repo import get_oauth_by_sub, link_oauth

router = APIRouter(prefix="/auth", tags=["auth-oauth"])


@router.get("/login/google")
async def login_google(request: Request, mode: str | None = None):
    redirect_uri = request.url_for("callback_google")
    return await oauth.google.authorize_redirect(
        request, f"{redirect_uri}?mode={mode or ''}"
    )


@router.get("/callback/google", name="callback_google")
async def callback_google(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    mode: str | None = None,
):
    token = await oauth.google.authorize_access_token(request)
    info = token.get("userinfo") or {}
    sub = info.get("sub")
    email = (info.get("email") or "").lower()
    email_verified = bool(info.get("email_verified"))
    name = info.get("name")
    if not sub:
        raise HTTPException(400, "No provider subject")

    if mode == "link":
        try:
            claims = decode_access(request)
        except Exception:
            raise HTTPException(401, "Login required to link")
        current_user_id = int(claims["sub"])
        existing = get_oauth_by_sub(db, "google", sub)
        if existing and existing.user_id != current_user_id:
            raise HTTPException(
                409, "This Google account is already linked to another user"
            )
        if not existing:
            link_oauth(db, current_user_id, "google", sub, email or None)
        return RedirectResponse(url=f"{settings.WEB_APP_URL}/settings/connections")

    # Sign-in or create+link
    try:
        user = signin_or_link_google(db, sub, email or None, email_verified, name)
    except ValueError as e:
        raise HTTPException(409, str(e))

    if not user.is_active:
        raise HTTPException(403, "Account disabled")

    access, refresh, jti = issue_tokens(sub=str(user.id))
    # TODO: store_refresh(...)
    set_auth_cookies(response, access, refresh)
    return RedirectResponse(url=settings.WEB_APP_URL)
