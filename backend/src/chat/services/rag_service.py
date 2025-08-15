"""RAG (Retrieval-Augmented Generation) service for enhanced chat responses."""

import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..repositories.rag_repository import RAGRepository
from src.core.logging import get_logger
from src.core.config import settings

logger = get_logger(__name__)


class RAGService:
    """Service for RAG operations to enhance chat responses with relevant context."""

    def __init__(self):
        self.rag_repo = RAGRepository()
        self.plant_namespace = "plant_knowledge"
        self.care_namespace = "plant_care"
        self.disease_namespace = "plant_diseases"

    async def get_relevant_context(
        self,
        query: str,
        plant_id: Optional[int] = None,
        conversation_history: Optional[List[str]] = None,
        max_tokens: int = 3000,
        min_score: float = 0.75
    ) -> List[Dict[str, Any]]:
        """Get relevant context for a user query."""
        try:
            # Enhance query with conversation context
            enhanced_query = await self._enhance_query_with_context(
                query, plant_id, conversation_history
            )

            # Query multiple namespaces in parallel
            contexts = []

            # General plant knowledge
            general_context = await self.rag_repo.get_relevant_context(
                query=enhanced_query,
                max_tokens=max_tokens // 3,
                top_k=5,
                score_threshold=min_score,
                namespace=self.plant_namespace
            )
            contexts.extend(general_context)

            # Plant care specific
            care_context = await self.rag_repo.get_relevant_context(
                query=enhanced_query,
                max_tokens=max_tokens // 3,
                top_k=5,
                score_threshold=min_score,
                namespace=self.care_namespace
            )
            contexts.extend(care_context)

            # Disease and problem diagnosis
            if any(word in query.lower() for word in ["sick", "dying", "problem", "disease", "pest", "brown", "yellow", "spots"]):
                disease_context = await self.rag_repo.get_relevant_context(
                    query=enhanced_query,
                    max_tokens=max_tokens // 3,
                    top_k=3,
                    score_threshold=min_score,
                    namespace=self.disease_namespace
                )
                contexts.extend(disease_context)

            # Sort by relevance score and remove duplicates
            unique_contexts = self._deduplicate_contexts(contexts)
            sorted_contexts = sorted(unique_contexts, key=lambda x: x.get("score", 0), reverse=True)

            logger.info(f"Retrieved {len(sorted_contexts)} relevant context items for query")
            return sorted_contexts[:10]  # Limit to top 10 most relevant

        except Exception as e:
            logger.error(f"Failed to get relevant context: {e}")
            return []

    async def index_plant_knowledge(
        self,
        knowledge_items: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Index plant knowledge into the vector database."""
        try:
            namespace = namespace or self.plant_namespace

            # Prepare documents for indexing
            documents = []
            for item in knowledge_items:
                doc_id = item.get("id") or f"doc_{int(time.time())}_{len(documents)}"
                text = item.get("text") or item.get("content", "")
                metadata = {
                    "source": item.get("source", "unknown"),
                    "category": item.get("category", "general"),
                    "plant_type": item.get("plant_type"),
                    "care_type": item.get("care_type"),
                    "difficulty_level": item.get("difficulty_level"),
                    "season": item.get("season"),
                    **item.get("metadata", {})
                }

                documents.append((doc_id, text, metadata))

            # Batch upsert to Pinecone
            result = await self.rag_repo.upsert_documents_batch(
                documents=documents,
                namespace=namespace
            )

            logger.info(f"Indexed {result['successful']} documents to namespace {namespace}")
            return result

        except Exception as e:
            logger.error(f"Failed to index plant knowledge: {e}")
            return {"successful": 0, "failed": len(knowledge_items), "error": str(e)}

    async def search_plant_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        plant_type: Optional[str] = None,
        top_k: int = 10,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search plant knowledge with filters."""
        try:
            # Build metadata filter
            filter_metadata = {}
            if category:
                filter_metadata["category"] = category
            if plant_type:
                filter_metadata["plant_type"] = plant_type

            # Query the knowledge base
            result = await self.rag_repo.query_similar_documents(
                query=query,
                top_k=top_k,
                score_threshold=score_threshold,
                namespace=self.plant_namespace,
                filter_metadata=filter_metadata if filter_metadata else None
            )

            return result.get("results", [])

        except Exception as e:
            logger.error(f"Plant knowledge search failed: {e}")
            return []

    async def get_plant_specific_context(
        self,
        plant_id: int,
        query: str,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get context specific to a user's plant."""
        try:
            # Import here to avoid circular imports
            from src.plants.service import PlantService

            plant_service = PlantService(db)
            plant = await plant_service.get_plant_by_id(plant_id)

            if not plant:
                return []

            # Enhance query with plant-specific information
            plant_query = f"{query} {plant.name} {plant.species or ''} {plant.variety or ''}"

            # Search for plant-specific information
            return await self.search_plant_knowledge(
                query=plant_query,
                plant_type=plant.species,
                top_k=5,
                score_threshold=0.8
            )

        except Exception as e:
            logger.error(f"Failed to get plant-specific context: {e}")
            return []

    async def update_knowledge_base(
        self,
        updates: List[Dict[str, Any]],
        namespace: Optional[str] = None
    ) -> bool:
        """Update existing knowledge in the vector database."""
        try:
            return await self.index_plant_knowledge(updates, namespace)
        except Exception as e:
            logger.error(f"Failed to update knowledge base: {e}")
            return False

    async def delete_knowledge_item(
        self,
        item_id: str,
        namespace: Optional[str] = None
    ) -> bool:
        """Delete a knowledge item from the vector database."""
        try:
            namespace = namespace or self.plant_namespace
            return await self.rag_repo.delete_document(item_id, namespace)
        except Exception as e:
            logger.error(f"Failed to delete knowledge item: {e}")
            return False

    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        try:
            stats = {}

            for namespace in [self.plant_namespace, self.care_namespace, self.disease_namespace]:
                namespace_stats = await self.rag_repo.get_namespace_stats(namespace)
                stats[namespace] = namespace_stats

            return stats

        except Exception as e:
            logger.error(f"Failed to get knowledge stats: {e}")
            return {"error": str(e)}

    async def _enhance_query_with_context(
        self,
        query: str,
        plant_id: Optional[int] = None,
        conversation_history: Optional[List[str]] = None
    ) -> str:
        """Enhance the query with conversation context."""
        enhanced_parts = [query]

        # Add recent conversation context
        if conversation_history:
            recent_context = " ".join(conversation_history[-3:])  # Last 3 messages
            enhanced_parts.append(recent_context)

        # Add plant context keywords based on query analysis
        query_lower = query.lower()

        if any(word in query_lower for word in ["water", "watering"]):
            enhanced_parts.append("watering frequency care schedule")

        if any(word in query_lower for word in ["light", "lighting", "sun"]):
            enhanced_parts.append("light requirements indoor placement")

        if any(word in query_lower for word in ["fertilize", "nutrients", "feed"]):
            enhanced_parts.append("fertilization nutrients feeding schedule")

        if any(word in query_lower for word in ["sick", "dying", "problem"]):
            enhanced_parts.append("plant health diagnosis symptoms treatment")

        return " ".join(enhanced_parts)

    def _deduplicate_contexts(self, contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate contexts based on content similarity."""
        if not contexts:
            return []

        unique_contexts = []
        seen_texts = set()

        for context in contexts:
            text = context.get("text", "")
            # Simple deduplication based on first 100 characters
            text_key = text[:100].lower().strip()

            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_contexts.append(context)

        return unique_contexts
