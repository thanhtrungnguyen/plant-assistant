from sqlalchemy.orm import Session
from src.auth.models import User, PasswordCredential, OAuthAccount


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).one_or_none()


def create_user(db: Session, email: str, name: str | None, verified: bool) -> User:
    user = User(email=email, name=name, email_verified=verified, is_active=True)
    db.add(user)
    db.flush()
    return user


def set_password(db: Session, user_id: int, password_hash: str):
    cred = db.get(PasswordCredential, user_id)
    if cred:
        cred.password_hash = password_hash
    else:
        db.add(PasswordCredential(user_id=user_id, password_hash=password_hash))
    db.commit()


def get_oauth_by_sub(
    db: Session, provider: str, provider_sub: str
) -> OAuthAccount | None:
    return (
        db.query(OAuthAccount)
        .filter_by(provider=provider, provider_sub=provider_sub)
        .one_or_none()
    )


def link_oauth(
    db: Session,
    user_id: int,
    provider: str,
    provider_sub: str,
    email_at_provider: str | None,
):
    db.add(
        OAuthAccount(
            user_id=user_id,
            provider=provider,
            provider_sub=provider_sub,
            email_at_provider=email_at_provider,
        )
    )
    db.commit()
