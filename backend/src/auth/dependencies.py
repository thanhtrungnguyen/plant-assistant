from fastapi import Request
from src.core.security import decode_access, verify_csrf


def require_user(request: Request):
    return decode_access(request)


def require_csrf(request: Request):
    verify_csrf(request)
