from fastapi import APIRouter
from datetime import datetime, timezone
from app.services.vector_store import vector_store_service

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    """Health check endpoint — returns system status."""
    try:
        sources = vector_store_service.list_sources()
        vector_db_status = "connected"
    except Exception as e:
        sources = []
        vector_db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "vector_db": vector_db_status,
        "documents_indexed": len(sources),
        "sources": sources,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
