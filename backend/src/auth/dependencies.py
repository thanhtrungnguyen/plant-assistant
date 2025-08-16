from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.security import decode_access, verify_csrf
from src.database.session import get_db
from src.auth.repositories.user_repo import get_user_by_id
from src.auth.models import User


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from JWT token."""
    token_data = decode_access(request)
    user_id = int(token_data["sub"])

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_csrf(request: Request):
    verify_csrf(request)
