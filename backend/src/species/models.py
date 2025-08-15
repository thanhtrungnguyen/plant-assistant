from __future__ import annotations

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models.base import DomainBase

"""Species reference model.

Usage:
- Identification: link candidates & sessions to canonical species data.
- Care Advice: provide default_care_json used as baseline for personalized plans.
- Search: uniqueness on scientific_name; index on common_name for user queries.
"""


class Species(DomainBase):
    __tablename__ = "species"
    __table_args__ = (
        UniqueConstraint("scientific_name", name="uq_species_scientific_name"),
        Index("ix_species_common_name", "common_name"),
    )

    scientific_name: Mapped[str] = mapped_column(String, index=True)
    common_name: Mapped[str | None] = mapped_column(String, index=True)
    synonyms: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    pet_safe: Mapped[bool | None] = mapped_column()
    default_care_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # id / created_at from DomainBase
