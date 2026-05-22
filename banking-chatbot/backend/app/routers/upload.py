import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.rag_pipeline import rag_pipeline
from app.models.document import UploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Upload"])

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and index a document (PDF, TXT, or DOCX) into the vector store.
    Max file size: 10MB.
    """
    # Validate filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    # Validate file extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file bytes
    file_bytes = await file.read()

    # Validate file size
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = len(file_bytes) / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f}MB). Maximum allowed size is 10MB."
        )

    logger.info(f"Received upload: {file.filename} ({len(file_bytes)} bytes)")

    # Run ingestion pipeline
    result = await rag_pipeline.ingest_document(file.filename, file_bytes)

    return UploadResponse(
        filename=result["filename"],
        chunks_indexed=result["chunks_count"],
        status=result["status"],
        message=result["message"],
    )
