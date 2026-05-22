import logging
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import chat, upload, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("=== Banking Chatbot API Starting Up ===")

    # Only initialize ChromaDB at startup (lightweight — no model loading)
    try:
        from app.services.vector_store import get_chroma_collection
        collection = get_chroma_collection()
        logger.info(f"ChromaDB initialized. Total chunks: {collection.count()}")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")

    # NOTE: Embedding model and document seeding are intentionally deferred
    # to the first request to stay within Render free tier 512MB RAM limit.
    # The first query/upload will be slower (~10s) as the model loads.

    logger.info("=== Banking Chatbot API Ready ===")
    yield
    logger.info("=== Banking Chatbot API Shutting Down ===")


async def _seed_sample_documents():
    """Auto-ingest sample documents from the data directory."""
    from app.services.rag_pipeline import rag_pipeline

    sample_docs_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sample_docs")
    sample_docs_dir = os.path.abspath(sample_docs_dir)

    if not os.path.isdir(sample_docs_dir):
        logger.warning(f"Sample docs directory not found: {sample_docs_dir}")
        return

    seeded = 0
    for filename in os.listdir(sample_docs_dir):
        if filename.endswith((".txt", ".pdf", ".docx")):
            filepath = os.path.join(sample_docs_dir, filename)
            try:
                with open(filepath, "rb") as f:
                    file_bytes = f.read()
                result = await rag_pipeline.ingest_document(filename, file_bytes)
                logger.info(f"Seeded: {filename} → {result['chunks_count']} chunks")
                seeded += 1
            except Exception as e:
                logger.error(f"Failed to seed {filename}: {e}")

    logger.info(f"Seeding complete. {seeded} documents indexed.")


# Create FastAPI app
app = FastAPI(
    title="Banking Support Chatbot API",
    description=(
        "A production-grade RAG-powered banking support chatbot. "
        "Upload documents and ask questions about loans, credit cards, and banking policies."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} → {response.status_code} ({duration:.1f}ms)"
    )
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again.",
            "path": str(request.url.path),
        },
    )


# Include routers
app.include_router(chat.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "Banking Support Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
