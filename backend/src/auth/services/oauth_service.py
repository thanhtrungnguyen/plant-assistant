from sqlalchemy.orm import Session
from src.auth.repositories import user_repo


def signin_or_link_google(
    db: Session,
    provider_sub: str,
    email: str | None,
    email_verified: bool,
    name: str | None,
):
    acct = user_repo.get_oauth_by_sub(db, "google", provider_sub)
    if acct:
        from src.auth.models import User

        return db.get(User, acct.user_id)

    user = user_repo.get_user_by_email(db, (email or "").lower()) if email else None
    if user:
        if not email_verified:
            raise ValueError("Email not verified by provider")
    else:
        verified = bool(email_verified and email)
        user = user_repo.create_user(
            db, email or f"google_{provider_sub}@example.invalid", name, verified
        )

    user_repo.link_oauth(db, user.id, "google", provider_sub, email)
    return user
