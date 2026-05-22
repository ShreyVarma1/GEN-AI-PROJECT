import logging
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)

_embedding_model = None


def get_embedding_model():
    """Singleton loader for the SentenceTransformer model."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully.")
    return _embedding_model


def _to_list(result) -> list:
    """Safely convert numpy array, tensor, or list to a plain Python list."""
    if hasattr(result, "tolist"):
        return result.tolist()
    if isinstance(result, list):
        # Each element might still be a numpy array or tensor
        return [_to_list(item) if hasattr(item, "tolist") else list(item) if hasattr(item, "__iter__") and not isinstance(item, (str, bytes)) else item for item in result]
    return list(result)


class EmbeddingService:
    """Generates vector embeddings using sentence-transformers (local, no API cost)."""

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text strings. Returns List[List[float]]."""
        if not texts:
            return []
        model = get_embedding_model()
        # encode() in newer sentence-transformers may return a list of tensors
        # Use convert_to_numpy=False to get consistent tensor output, then convert
        result = model.encode(texts, show_progress_bar=False, convert_to_numpy=False)
        # result is either a numpy array, a tensor, or a list — normalise to list of lists
        if hasattr(result, "tolist"):
            return result.tolist()
        # It's a list/sequence of per-text embeddings
        output = []
        for emb in result:
            if hasattr(emb, "tolist"):
                output.append(emb.tolist())
            elif hasattr(emb, "numpy"):
                output.append(emb.numpy().tolist())
            else:
                output.append(list(emb))
        return output

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string. Returns List[float]."""
        model = get_embedding_model()
        result = model.encode([query], show_progress_bar=False, convert_to_numpy=False)
        # result is a batch of 1 — get the first element
        if hasattr(result, "tolist"):
            return result.tolist()[0]
        emb = result[0]
        if hasattr(emb, "tolist"):
            return emb.tolist()
        elif hasattr(emb, "numpy"):
            return emb.numpy().tolist()
        return list(emb)


embedding_service = EmbeddingService()
