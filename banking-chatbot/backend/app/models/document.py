from pydantic import BaseModel
from typing import Optional


class UploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    status: str
    message: str


class DocumentInfo(BaseModel):
    source: str
    chunks_count: Optional[int] = None
