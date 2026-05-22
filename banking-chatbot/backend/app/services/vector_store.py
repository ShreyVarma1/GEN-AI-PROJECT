import logging
import hashlib
from typing import List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

_chroma_client = None
_collection = None


def get_chroma_collection():
    """Singleton ChromaDB collection."""
    global _chroma_client, _collection
    if _collection is None:
        import chromadb
        logger.info(f"Initializing ChromaDB at: {settings.CHROMA_PERSIST_DIR}")
        _chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        _collection = _chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB collection '{settings.CHROMA_COLLECTION_NAME}' ready. "
                    f"Documents: {_collection.count()}")
    return _collection


class VectorStoreService:
    """Manages ChromaDB vector storage and retrieval."""

    def add_documents(
        self,
        chunks,  # List[LangChainDocument]
        embeddings: List[List[float]],
        source_name: str,
    ) -> int:
        """Upsert document chunks with embeddings into ChromaDB."""
        collection = get_chroma_collection()
        if not chunks or not embeddings:
            return 0

        ids = []
        documents = []
        metadatas = []
        valid_embeddings = []

        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = f"{source_name}_{chunk.metadata['chunk_index']}"
            # Use deterministic hash-based ID to avoid duplicates
            stable_id = hashlib.md5(chunk_id.encode()).hexdigest()
            ids.append(stable_id)
            documents.append(chunk.page_content)
            metadatas.append({
                "source": chunk.metadata.get("source", source_name),
                "chunk_index": chunk.metadata.get("chunk_index", 0),
                "page_hint": chunk.metadata.get("page_hint", ""),
                "char_count": chunk.metadata.get("char_count", len(chunk.page_content)),
            })
            valid_embeddings.append(embedding)

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=valid_embeddings,
            metadatas=metadatas,
        )
        logger.info(f"Upserted {len(ids)} chunks for source: {source_name}")
        return len(ids)

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        source_filter: Optional[str] = None,
    ) -> List[dict]:
        """Return top-K similar chunks with metadata and distance."""
        collection = get_chroma_collection()
        if collection.count() == 0:
            return []

        where_filter = {"source": source_filter} if source_filter else None
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        if results and results.get("documents"):
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                chunks.append({
                    "text": doc,
                    "metadata": meta,
                    "distance": round(dist, 4),
                })
        return chunks

    def list_sources(self) -> List[str]:
        """Return unique source filenames in the collection."""
        collection = get_chroma_collection()
        if collection.count() == 0:
            return []
        results = collection.get(include=["metadatas"])
        sources = set()
        for meta in results.get("metadatas", []):
            if meta and "source" in meta:
                sources.add(meta["source"])
        return sorted(list(sources))

    def delete_source(self, source_name: str) -> int:
        """Delete all chunks belonging to a source document."""
        collection = get_chroma_collection()
        results = collection.get(
            where={"source": source_name},
            include=["metadatas"],
        )
        ids_to_delete = results.get("ids", [])
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            logger.info(f"Deleted {len(ids_to_delete)} chunks for source: {source_name}")
        return len(ids_to_delete)

    def get_collection_count(self) -> int:
        """Return total number of chunks stored."""
        return get_chroma_collection().count()


vector_store_service = VectorStoreService()
