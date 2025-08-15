"""Repository for RAG (Retrieval-Augmented Generation) operations with Pinecone."""

import time
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI

from src.core.config import settings
from src.core.logging import get_logger
from src.database.pinecone import get_pinecone
from src.integrations.openai_api.openai_api import get_openai_client

logger = get_logger(__name__)


class RAGRepository:
    """Repository for RAG operations using Pinecone and OpenAI."""

    def __init__(self):
        self.pinecone_client = get_pinecone()
        self.openai_client = get_openai_client()
        self.default_index = settings.PINECONE_DEFAULT_INDEX
        self.default_namespace = settings.PINECONE_DEFAULT_NAMESPACE or "plant_knowledge"

    def _get_index(self, index_name: Optional[str] = None):
        """Get Pinecone index instance."""
        if not self.pinecone_client:
            raise ValueError("Pinecone client not configured")

        index_name = index_name or self.default_index
        if not index_name:
            raise ValueError("No Pinecone index specified")

        return self.pinecone_client.Index(index_name)

    async def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """Generate embedding for text using OpenAI."""
        if not self.openai_client:
            raise ValueError("OpenAI client not configured")

        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    async def upsert_document(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        index_name: Optional[str] = None
    ) -> bool:
        """Upsert a document to Pinecone."""
        try:
            # Generate embedding
            embedding = await self.generate_embedding(text)

            # Prepare metadata
            final_metadata = metadata or {}
            final_metadata.update({
                "text": text,
                "created_at": time.time()
            })

            # Upsert to Pinecone
            index = self._get_index(index_name)
            namespace = namespace or self.default_namespace

            index.upsert(
                vectors=[(doc_id, embedding, final_metadata)],
                namespace=namespace
            )

            logger.info(f"Successfully upserted document {doc_id} to namespace {namespace}")
            return True

        except Exception as e:
            logger.error(f"Failed to upsert document {doc_id}: {e}")
            return False

    async def upsert_documents_batch(
        self,
        documents: List[Tuple[str, str, Optional[Dict[str, Any]]]],
        namespace: Optional[str] = None,
        index_name: Optional[str] = None,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """Upsert multiple documents in batches."""
        try:
            namespace = namespace or self.default_namespace
            index = self._get_index(index_name)

            successful = 0
            failed = 0

            # Process in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                vectors = []

                for doc_id, text, metadata in batch:
                    try:
                        embedding = await self.generate_embedding(text)
                        final_metadata = metadata or {}
                        final_metadata.update({
                            "text": text,
                            "created_at": time.time()
                        })
                        vectors.append((doc_id, embedding, final_metadata))

                    except Exception as e:
                        logger.error(f"Failed to process document {doc_id}: {e}")
                        failed += 1
                        continue

                if vectors:
                    try:
                        index.upsert(vectors=vectors, namespace=namespace)
                        successful += len(vectors)

                    except Exception as e:
                        logger.error(f"Failed to upsert batch: {e}")
                        failed += len(vectors)

            return {
                "successful": successful,
                "failed": failed,
                "total": len(documents)
            }

        except Exception as e:
            logger.error(f"Batch upsert failed: {e}")
            return {"successful": 0, "failed": len(documents), "total": len(documents)}

    async def query_similar_documents(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
        namespace: Optional[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        index_name: Optional[str] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Query similar documents from Pinecone."""
        start_time = time.time()

        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)

            # Query Pinecone
            index = self._get_index(index_name)
            namespace = namespace or self.default_namespace

            response = index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter=filter_metadata,
                include_metadata=include_metadata
            )

            # Filter by score threshold
            filtered_matches = [
                match for match in response.matches
                if match.score >= score_threshold
            ]

            # Format results
            results = []
            for match in filtered_matches:
                result = {
                    "id": match.id,
                    "score": match.score,
                }

                if include_metadata and match.metadata:
                    result["metadata"] = match.metadata
                    result["text"] = match.metadata.get("text", "")

                results.append(result)

            processing_time = time.time() - start_time

            return {
                "results": results,
                "query_embedding": query_embedding if include_metadata else None,
                "processing_time": processing_time,
                "total_matches": len(response.matches),
                "filtered_matches": len(filtered_matches)
            }

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "results": [],
                "query_embedding": None,
                "processing_time": time.time() - start_time,
                "error": str(e)
            }

    async def get_relevant_context(
        self,
        query: str,
        max_tokens: int = 4000,
        top_k: int = 10,
        score_threshold: float = 0.7,
        namespace: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get relevant context for RAG, respecting token limits."""
        try:
            # Query for similar documents
            query_result = await self.query_similar_documents(
                query=query,
                top_k=top_k,
                score_threshold=score_threshold,
                namespace=namespace
            )

            results = query_result.get("results", [])
            if not results:
                return []

            # Select context while respecting token limits
            selected_context = []
            current_tokens = 0

            for result in results:
                text = result.get("text", "")
                if not text:
                    continue

                # Rough token estimation (4 chars per token)
                estimated_tokens = len(text) // 4

                if current_tokens + estimated_tokens <= max_tokens:
                    selected_context.append({
                        "text": text,
                        "score": result["score"],
                        "metadata": result.get("metadata", {}),
                        "source_id": result["id"]
                    })
                    current_tokens += estimated_tokens
                else:
                    break

            logger.info(f"Selected {len(selected_context)} context items, ~{current_tokens} tokens")
            return selected_context

        except Exception as e:
            logger.error(f"Failed to get relevant context: {e}")
            return []

    async def delete_document(
        self,
        doc_id: str,
        namespace: Optional[str] = None,
        index_name: Optional[str] = None
    ) -> bool:
        """Delete a document from Pinecone."""
        try:
            index = self._get_index(index_name)
            namespace = namespace or self.default_namespace

            index.delete(
                ids=[doc_id],
                namespace=namespace
            )

            logger.info(f"Successfully deleted document {doc_id} from namespace {namespace}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    async def clear_namespace(
        self,
        namespace: str,
        index_name: Optional[str] = None
    ) -> bool:
        """Clear all documents from a namespace."""
        try:
            index = self._get_index(index_name)

            index.delete(
                delete_all=True,
                namespace=namespace
            )

            logger.info(f"Successfully cleared namespace {namespace}")
            return True

        except Exception as e:
            logger.error(f"Failed to clear namespace {namespace}: {e}")
            return False

    async def get_namespace_stats(
        self,
        namespace: Optional[str] = None,
        index_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get statistics for a namespace."""
        try:
            index = self._get_index(index_name)
            namespace = namespace or self.default_namespace

            stats = index.describe_index_stats()

            # Get namespace-specific stats if available
            namespace_stats = stats.namespaces.get(namespace, {})

            return {
                "namespace": namespace,
                "vector_count": namespace_stats.get("vector_count", 0),
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }

        except Exception as e:
            logger.error(f"Failed to get namespace stats: {e}")
            return {"error": str(e)}
