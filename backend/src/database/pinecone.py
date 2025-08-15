"""Pinecone vector database utilities.

Provides a singleton-like accessor to a Pinecone client and convenience
helpers for upserting and querying vectors used by `VectorItem` records.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence, cast

from pinecone import Pinecone, ServerlessSpec

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

_pc: Pinecone | None = None


def get_pinecone() -> Pinecone | None:
    """Return a cached Pinecone client instance or None if not configured."""
    global _pc
    if _pc is not None:
        return _pc
    if not settings.PINECONE_API_KEY:
        logger.warning("Pinecone not configured: missing PINECONE_API_KEY")
        return None
    _pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    return _pc


def ensure_index(
    name: str | None = None, dimension: int = 1536, metric: str = "cosine"
) -> str | None:
    """Ensure an index exists; create serverless index if absent.

    Returns the index name or None if client not configured.
    """
    pc = get_pinecone()
    if pc is None:
        return None
    index_name = name or settings.PINECONE_DEFAULT_INDEX
    if not index_name:
        logger.warning("No Pinecone index name provided or configured")
        return None
    existing = {idx["name"] for idx in pc.list_indexes()}
    if index_name not in existing:
        logger.info(
            f"Creating Pinecone index '{index_name}' (dim={dimension}, metric={metric})"
        )
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return index_name


def upsert_vectors(
    items: Sequence[tuple[str, list[float], dict | None]],
    index_name: str | None = None,
    namespace: str | None = None,
):
    """Upsert a batch of vectors.

    items: list of tuples (id, embedding, metadata)
    metadata must be JSON-serializable.
    Returns count of upserted vectors or 0 if not configured.
    """
    pc = get_pinecone()
    if pc is None:
        return 0
    index_name = index_name or settings.PINECONE_DEFAULT_INDEX
    namespace = namespace or settings.PINECONE_DEFAULT_NAMESPACE
    if not index_name:
        logger.warning("Cannot upsert vectors: index name not set")
        return 0
    ensure_index(index_name)
    index = pc.Index(index_name)
    to_upsert = []
    for vid, emb, meta in items:
        vec = {"id": vid, "values": emb}
        if meta:
            vec["metadata"] = meta
        to_upsert.append(vec)
    index.upsert(vectors=to_upsert, namespace=namespace)
    return len(to_upsert)


def fetch_vectors(
    ids: Iterable[str], index_name: str | None = None, namespace: str | None = None
):
    pc = get_pinecone()
    if pc is None:
        return {}
    index_name = index_name or settings.PINECONE_DEFAULT_INDEX
    namespace = namespace or settings.PINECONE_DEFAULT_NAMESPACE
    if not index_name:
        return {}
    index = pc.Index(index_name)
    return index.fetch(ids=list(ids), namespace=namespace)


def query_vector(
    embedding: list[float],
    top_k: int = 5,
    filter: dict | None = None,
    index_name: str | None = None,
    namespace: str | None = None,
):
    pc = get_pinecone()
    if pc is None:
        return []
    index_name = index_name or settings.PINECONE_DEFAULT_INDEX
    namespace = namespace or settings.PINECONE_DEFAULT_NAMESPACE
    if not index_name:
        return []
    index = pc.Index(index_name)
    res: Any = index.query(
        vector=embedding,
        top_k=top_k,
        filter=filter,
        namespace=namespace,
        include_metadata=True,
    )
    return cast(list[Any], getattr(res, "matches", []))
