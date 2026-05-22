import logging
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generates vector embeddings using Google's text-embedding-004 model.
    Free via Google AI Studio — same API key as Gemini.
    Produces 768-dimensional vectors.
    No local model download required — ideal for free-tier cloud deployment.
    """

    def _get_genai(self):
        import google.generativeai as genai
        if not settings.GOOGLE_API_KEY:
            raise RuntimeError("GOOGLE_API_KEY is not set.")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        return genai

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text strings. Returns List[List[float]]."""
        if not texts:
            return []
        genai = self._get_genai()
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
            )
            embeddings.append(result["embedding"])
        logger.info(f"Embedded {len(texts)} texts via Google text-embedding-004")
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string. Returns List[float]."""
        genai = self._get_genai()
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query",
        )
        return result["embedding"]


embedding_service = EmbeddingService()
