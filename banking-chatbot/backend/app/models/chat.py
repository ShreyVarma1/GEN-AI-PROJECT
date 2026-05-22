from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)
    stream: bool = False

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v.strip()


class SourceChunk(BaseModel):
    filename: str
    chunk_preview: str
    distance: Optional[float] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[SourceChunk] = []
    tokens_used: Optional[int] = None
