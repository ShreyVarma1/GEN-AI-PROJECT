import logging
import httpx
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generates vector embeddings using Google's text-embedding-004 model via REST API.
    Free via Google AI Studio — same API key as Gemini.
    Produces 768-dimensional vectors.
    Uses httpx directly for reliable async HTTP calls.
    """

    def _embed_single(self, text: str, task_type: str = "retrieval_document") -> List[float]:
        """Embed a single text synchronously via REST."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={settings.GOOGLE_API_KEY}"
        payload = {
            "model": "models/text-embedding-004",
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()["embedding"]["values"]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text strings. Returns List[List[float]]."""
        if not texts:
            return []
        embeddings = []
        for i, text in enumerate(texts):
            emb = self._embed_single(text, task_type="RETRIEVAL_DOCUMENT")
            embeddings.append(emb)
            if (i + 1) % 10 == 0:
                logger.info(f"Embedded {i + 1}/{len(texts)} chunks...")
        logger.info(f"Embedded {len(texts)} texts via Google text-embedding-004")
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string. Returns List[float]."""
        return self._embed_single(query, task_type="RETRIEVAL_QUERY")


embedding_service = EmbeddingService()
