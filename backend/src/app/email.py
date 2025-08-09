from pathlib import Path
import urllib.parse
from typing import Optional

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from .config import settings
from .models import User


def get_email_config() -> Optional[ConnectionConfig]:
    """Get email configuration if all required settings are provided."""
    if not all(
        [
            settings.MAIL_USERNAME,
            settings.MAIL_PASSWORD,
            settings.MAIL_FROM,
            settings.MAIL_SERVER,
            settings.MAIL_PORT,
        ]
    ):
        return None

    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,  # type: ignore
        MAIL_PASSWORD=settings.MAIL_PASSWORD,  # type: ignore
        MAIL_FROM=settings.MAIL_FROM,  # type: ignore
        MAIL_PORT=settings.MAIL_PORT,  # type: ignore
        MAIL_SERVER=settings.MAIL_SERVER,  # type: ignore
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.USE_CREDENTIALS,
        VALIDATE_CERTS=settings.VALIDATE_CERTS,
        TEMPLATE_FOLDER=Path(__file__).parent / settings.TEMPLATE_DIR,
    )
    return conf


async def send_reset_password_email(user: User, token: str) -> None:
    conf = get_email_config()
    if conf is None:
        # Email not configured, skip sending
        return

    email = user.email
    base_url = f"{settings.FRONTEND_URL}/password-recovery/confirm?"
    params = {"token": token}
    encoded_params = urllib.parse.urlencode(params)
    link = f"{base_url}{encoded_params}"
    message = MessageSchema(
        subject="Password recovery",
        recipients=[email],
        template_body={"username": email, "link": link},
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="password_reset.html")
