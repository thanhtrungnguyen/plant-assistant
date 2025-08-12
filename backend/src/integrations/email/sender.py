from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.core.config import settings

# Jinja2 environment
_templates_dir = Path(settings.TEMPLATE_DIR)
_jinja = Environment(
    loader=FileSystemLoader(str(_templates_dir)),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_template(name: str, context: Dict[str, Any]) -> tuple[str, str]:
    """Return (text, html) from templates located under TEMPLATE_DIR.
    Expected files: f"{name}.txt.j2" and optionally f"{name}.html.j2".
    """
    txt_tmpl = _jinja.get_template(f"{name}.txt.j2")
    txt = txt_tmpl.render(**context)
    try:
        html = _jinja.get_template(f"{name}.html.j2").render(**context)
    except Exception:
        html = ""
    return txt, html


def _build_message(
    to_email: str, subject: str, text: str, html: str = ""
) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = (
        f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
        if settings.MAIL_FROM
        else settings.MAIL_FROM_NAME
    )
    msg["To"] = to_email
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")
    return msg


def _smtp_send(msg: EmailMessage) -> None:
    host = settings.MAIL_SERVER or "localhost"
    port = settings.MAIL_PORT or (465 if settings.MAIL_SSL_TLS else 25)

    if settings.MAIL_SSL_TLS:
        context = (
            ssl.create_default_context()
            if settings.VALIDATE_CERTS
            else ssl._create_unverified_context()
        )
        with smtplib.SMTP_SSL(host, port, context=context) as s:
            if (
                settings.USE_CREDENTIALS
                and settings.MAIL_USERNAME
                and settings.MAIL_PASSWORD
            ):
                s.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            s.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as s:
            if settings.MAIL_STARTTLS:
                context = (
                    ssl.create_default_context()
                    if settings.VALIDATE_CERTS
                    else ssl._create_unverified_context()
                )
                s.starttls(context=context)
            if (
                settings.USE_CREDENTIALS
                and settings.MAIL_USERNAME
                and settings.MAIL_PASSWORD
            ):
                s.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            s.send_message(msg)


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    context = {
        "reset_link": reset_link,
        "from_name": settings.MAIL_FROM_NAME,
        "app_url": getattr(settings, "WEB_APP_URL", ""),
        "minutes": getattr(settings, "PASSWORD_RESET_MINUTES", 30),
    }
    text, html = render_template("password_reset", context)
    msg = _build_message(to_email, "Reset your password", text, html)

    if not settings.MAIL_SERVER:
        # Dev fallback: print to console if mail is not configured
        print("[DEV EMAIL] To:", to_email, "\n", msg)
        return

    _smtp_send(msg)
