from __future__ import annotations

from datetime import datetime


from core.models.base import DomainBase
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

"""Consent audit log for GDPR compliance.

Tracks grant & revoke timestamps per consent_type for each user.
"""


class AuditConsentLog(DomainBase):
    __tablename__ = "audit_consent_logs"
    # id / created_at from DomainBase
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    consent_type: Mapped[str] = mapped_column(String(40))
    granted_at: Mapped[datetime]
    revoked_at: Mapped[datetime | None]
