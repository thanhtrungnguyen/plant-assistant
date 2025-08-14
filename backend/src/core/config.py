import os

from pathlib import Path
from typing import Set

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "plant-assistant"
    # OpenAPI docs
    OPENAPI_URL: str = "/openapi.json"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"
    TEST_DATABASE_URL: str | None = None
    EXPIRE_ON_COMMIT: bool = False

    # User
    ACCESS_SECRET_KEY: str = "your-secret-key"
    RESET_PASSWORD_SECRET_KEY: str = "your-reset-secret-key"
    VERIFICATION_SECRET_KEY: str = "your-verification-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600

    JWT_SECRET: str | None = None
    ACCESS_MIN: int = 20
    REFRESH_DAYS: int = 14

    COOKIE_DOMAIN: str = ".example.com"
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "lax"
    CSRF_COOKIE_NAME: str = "csrf_token"

    # Email
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = None
    MAIL_SERVER: str | None = None
    MAIL_PORT: int | None = None
    MAIL_FROM_NAME: str = "FastAPI template"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_DIR: str = "email_templates"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Google OAuth
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    # Password reset config
    PASSWORD_RESET_MINUTES: int = 30
    EMAIL_FROM: str = "no-reply@example.com"
    EMAIL_FROM_NAME: str = "Support"

    # SMTP (or set these to use a local mailer/dev null)
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_USE_TLS: bool = True

    # CORS
    CORS_ORIGINS: Set[str] = {"http://localhost:3000"}

    # AI/OpenAI Configuration
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_VISION_MODEL: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", 1500))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", 0.1))
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "66ae9620c64d4036a01131409251208")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
