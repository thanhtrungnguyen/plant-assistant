from __future__ import annotations

from typing import Sequence

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core.config import settings
from src.core.models.base import DomainBase
from src.database import pinecone

"""Vector index tracking model.

Feature integration:
- Identification & Diagnosis: semantic similarity lookups via Pinecone (collection selects corpus).
- Care Advice: future retrieval-augmented generation using stored embeddings.
- Metadata JSON used for filtering & re-ranking (e.g., taxonomic family, issue category).
"""


class VectorItem(DomainBase):
    __tablename__ = "vector_items"
    __table_args__ = (
        Index("ix_vector_items_collection", "collection"),
        UniqueConstraint(
            "collection", "external_vector_id", name="uq_vector_collection_external_id"
        ),
    )

    # id / created_at from DomainBase
    collection: Mapped[str] = mapped_column(String(50))
    external_vector_id: Mapped[str] = mapped_column(String(100))
    source_kind: Mapped[str | None] = mapped_column(String(30))
    source_id: Mapped[int | None]
    vector_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # created_at from DomainBase

    # --- Vector DB helpers -------------------------------------------------
    @staticmethod
    def upsert_batch(
        items: Sequence["VectorItem"],
        embeddings: dict[int, list[float]],
        index_name: str | None = None,
        namespace: str | None = None,
    ) -> int:
        """Upsert a batch of VectorItem rows + embeddings to Pinecone.

        embeddings: mapping of VectorItem.id -> embedding list
        Returns number of vectors upserted.
        """
        if not embeddings:
            return 0
        index_name = index_name or settings.PINECONE_DEFAULT_INDEX
        namespace = namespace or settings.PINECONE_DEFAULT_NAMESPACE
        payload = []
        for item in items:
            emb = embeddings.get(item.id)
            if not emb:
                continue
            meta = {
                "collection": item.collection,
                "source_kind": item.source_kind,
                "source_id": item.source_id,
                **(item.vector_metadata or {}),
            }
            payload.append((str(item.id), emb, meta))
        if not payload:
            return 0
        return pinecone.upsert_vectors(
            payload, index_name=index_name, namespace=namespace
        )

    @staticmethod
    def query(
        embedding: list[float],
        top_k: int = 5,
        filter: dict | None = None,
        index_name: str | None = None,
        namespace: str | None = None,
    ):
        return pinecone.query_vector(
            embedding=embedding,
            top_k=top_k,
            filter=filter,
            index_name=index_name or settings.PINECONE_DEFAULT_INDEX,
            namespace=namespace or settings.PINECONE_DEFAULT_NAMESPACE,
        )
