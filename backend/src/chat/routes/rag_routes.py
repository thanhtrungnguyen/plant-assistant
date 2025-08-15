"""RAG (Retrieval-Augmented Generation) API routes for knowledge management."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from src.auth.dependencies import require_user
from src.auth.models import User
from ..schemas import RAGQueryRequest, RAGQueryResponse
from ..services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["RAG Knowledge"])


def get_rag_service() -> RAGService:
    """Get RAG service instance."""
    return RAGService()


class KnowledgeItem(BaseModel):
    """Schema for knowledge items to be indexed."""
    id: Optional[str] = None
    text: str
    source: Optional[str] = "user_upload"
    category: Optional[str] = "general"
    plant_type: Optional[str] = None
    care_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    season: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeIndexResponse(BaseModel):
    """Response for knowledge indexing operations."""
    successful: int
    failed: int
    total: int
    message: str


@router.post("/query", response_model=RAGQueryResponse)
async def query_knowledge_base(
    request: RAGQueryRequest,
    current_user: User = Depends(require_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Query the plant knowledge base using semantic search.

    This endpoint allows users to search for relevant plant care information
    using natural language queries. It returns similar documents with confidence scores.
    """
    try:
        result = await rag_service.search_plant_knowledge(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold
        )

        return RAGQueryResponse(
            results=result,
            processing_time=0.0  # This would be calculated in the service
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to query knowledge base")


@router.post("/knowledge", response_model=KnowledgeIndexResponse)
async def index_plant_knowledge(
    knowledge_items: List[KnowledgeItem],
    namespace: Optional[str] = Query("plant_knowledge", description="Knowledge namespace"),
    current_user: User = Depends(require_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Index plant knowledge into the vector database.

    This endpoint allows authorized users to add new plant care knowledge
    to the system's knowledge base. The knowledge is vectorized and stored
    for use in RAG-enhanced chat responses.
    """
    try:
        # Convert Pydantic models to dictionaries
        knowledge_dicts = [item.model_dump() for item in knowledge_items]

        result = await rag_service.index_plant_knowledge(
            knowledge_items=knowledge_dicts,
            namespace=namespace
        )

        return KnowledgeIndexResponse(
            successful=result["successful"],
            failed=result["failed"],
            total=result["total"],
            message=f"Successfully indexed {result['successful']} items"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to index knowledge")


@router.get("/knowledge/search")
async def search_plant_knowledge(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    plant_type: Optional[str] = Query(None, description="Filter by plant type"),
    top_k: int = Query(10, ge=1, le=50, description="Number of results"),
    score_threshold: float = Query(0.7, ge=0, le=1, description="Minimum similarity score"),
    current_user: User = Depends(require_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Search plant knowledge with optional filters.

    This endpoint provides advanced search capabilities with category
    and plant type filters for more targeted results.
    """
    try:
        results = await rag_service.search_plant_knowledge(
            query=query,
            category=category,
            plant_type=plant_type,
            top_k=top_k,
            score_threshold=score_threshold
        )

        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "filters": {
                "category": category,
                "plant_type": plant_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search knowledge")


@router.delete("/knowledge/{item_id}")
async def delete_knowledge_item(
    item_id: str,
    namespace: Optional[str] = Query("plant_knowledge", description="Knowledge namespace"),
    current_user: User = Depends(require_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """Delete a knowledge item from the vector database."""
    try:
        success = await rag_service.delete_knowledge_item(item_id, namespace)

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found")

        return {"message": f"Successfully deleted knowledge item {item_id}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete knowledge item")


@router.get("/stats")
async def get_knowledge_stats(
    current_user: User = Depends(require_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """Get statistics about the knowledge base."""
    try:
        stats = await rag_service.get_knowledge_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve knowledge stats")


# Health check for RAG service
@router.get("/health")
async def rag_service_health():
    """Health check for RAG service."""
    try:
        rag_service = get_rag_service()
        # Basic connectivity check
        stats = await rag_service.get_knowledge_stats()

        return {
            "status": "healthy",
            "service": "rag",
            "features": [
                "semantic_search",
                "knowledge_indexing",
                "vector_storage",
                "context_retrieval"
            ],
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "rag",
            "error": str(e)
        }
