from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from src.auth.repositories import user_repo
from src.auth.models import PasswordCredential


def register_email_password(db: Session, email: str, password: str, name: str | None):
    email = email.lower()
    if user_repo.get_user_by_email(db, email):
        raise ValueError("Email already in use")
    user = user_repo.create_user(db, email, name, verified=False)
    user_repo.set_password(db, user.id, bcrypt.hash(password))
    # TODO: send verification email
    return user


def login_email_password(db: Session, email: str, password: str):
    email = email.lower()
    user = user_repo.get_user_by_email(db, email)
    if not user:
        return None

    cred = db.get(PasswordCredential, user.id)
    if not cred or not bcrypt.verify(password, cred.password_hash):
        return None
    return user if user.is_active else None
