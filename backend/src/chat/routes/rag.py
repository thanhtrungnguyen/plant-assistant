"""RAG (Retrieval-Augmented Generation) API routes."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth.dependencies import require_user
from src.auth.models import User
from src.database.session import get_db
from ..schemas import RAGQueryRequest, RAGQueryResponse
from ..services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["RAG Knowledge Base"])


def get_rag_service() -> RAGService:
    """Get RAG service instance."""
    return RAGService()


@router.post("/query", response_model=RAGQueryResponse)
async def query_knowledge_base(
    request: RAGQueryRequest,
    current_user: User = Depends(require_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Query the plant knowledge base using semantic search.

    This endpoint allows users to search through the indexed plant care knowledge
    using natural language queries with semantic similarity matching.
    """
    try:
        result = await rag_service.search_plant_knowledge(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold
        )

        return RAGQueryResponse(
            results=result,
            processing_time=0.1  # Will be calculated in actual implementation
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Knowledge base query failed: {str(e)}"
        )


@router.post("/knowledge/index")
async def index_plant_knowledge(
    knowledge_items: List[Dict[str, Any]],
    namespace: Optional[str] = Query(None, description="Target namespace for indexing"),
    current_user: User = Depends(require_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """
    Index new plant knowledge into the vector database.

    This endpoint allows administrators to add new plant care knowledge
    that will be available for RAG-enhanced chat responses.
    """
    try:
        result = await rag_service.index_plant_knowledge(
            knowledge_items=knowledge_items,
            namespace=namespace
        )

        return {
            "message": f"Successfully indexed {result['successful']} items",
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Knowledge indexing failed: {str(e)}"
        )


@router.get("/knowledge/stats")
async def get_knowledge_base_stats(
    current_user: User = Depends(require_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """Get statistics about the knowledge base."""
    try:
        stats = await rag_service.get_knowledge_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge base stats: {str(e)}"
        )


@router.delete("/knowledge/{item_id}")
async def delete_knowledge_item(
    item_id: str,
    namespace: Optional[str] = Query(None, description="Namespace containing the item"),
    current_user: User = Depends(require_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """Delete a knowledge item from the vector database."""
    try:
        success = await rag_service.delete_knowledge_item(item_id, namespace)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge item not found"
            )

        return {"message": f"Successfully deleted knowledge item {item_id}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete knowledge item: {str(e)}"
        )


@router.get("/search")
async def search_plant_knowledge(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    plant_type: Optional[str] = Query(None, description="Filter by plant type"),
    top_k: int = Query(10, ge=1, le=50, description="Number of results"),
    score_threshold: float = Query(0.7, ge=0, le=1, description="Minimum similarity score"),
    current_user: User = Depends(require_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    """Search plant knowledge with filters."""
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
            "filters": {
                "category": category,
                "plant_type": plant_type
            },
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


# Health check for RAG service
@router.get("/health")
async def rag_service_health():
    """Health check for RAG service."""
    try:
        # Basic health check
        rag_service = RAGService()

        # Try to get stats to verify connection
        stats = await rag_service.get_knowledge_stats()

        return {
            "status": "healthy",
            "service": "rag",
            "features": [
                "semantic_search",
                "knowledge_indexing",
                "vector_database",
                "openai_embeddings"
            ],
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "rag",
            "error": str(e)
        }
