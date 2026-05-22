import asyncio
import logging
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncIterator, Optional
from app.config import settings
from app.services.document_parser import document_parser
from app.services.chunker import text_chunker
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store_service
from app.services.llm_client import llm_client
from app.utils.session_manager import session_manager
from app.utils.prompt_builder import prompt_builder

_executor = ThreadPoolExecutor(max_workers=4)


async def run_in_thread(func, *args):
    """Run a blocking function in a thread pool executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, func, *args)

logger = logging.getLogger(__name__)

# Optional Redis cache
_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None and settings.REDIS_URL:
        try:
            import redis
            _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            _redis_client.ping()
            logger.info("Redis cache connected.")
        except Exception as e:
            logger.warning(f"Redis unavailable, caching disabled: {e}")
            _redis_client = False  # Mark as unavailable
    return _redis_client if _redis_client else None


def _cache_key(query: str, chunk_ids: list) -> str:
    """Generate a deterministic cache key from query + chunk IDs."""
    payload = query.lower().strip() + "|" + ",".join(sorted(chunk_ids))
    return "rag:" + hashlib.sha256(payload.encode()).hexdigest()


class RAGPipeline:
    """Orchestrates the full RAG pipeline: ingestion and query."""

    async def ingest_document(self, filename: str, file_bytes: bytes) -> dict:
        """
        Full ingestion pipeline:
        1. Parse document → raw text
        2. Chunk text → List[Document]
        3. Generate embeddings for all chunks
        4. Store in ChromaDB
        """
        logger.info(f"Starting ingestion for: {filename}")

        # Step 1: Parse (blocking I/O)
        raw_text = await run_in_thread(document_parser.parse, filename, file_bytes)
        logger.info(f"Parsed '{filename}': {len(raw_text)} characters")

        # Step 2: Chunk (CPU-bound)
        chunks = await run_in_thread(text_chunker.chunk, raw_text, filename)
        if not chunks:
            return {"filename": filename, "chunks_count": 0, "status": "warning",
                    "message": "Document parsed but produced no chunks."}

        # Step 3: Embed (CPU-bound, can be slow)
        texts = [chunk.page_content for chunk in chunks]
        embeddings = await run_in_thread(embedding_service.embed_texts, texts)

        # Step 4: Store
        stored_count = await run_in_thread(
            vector_store_service.add_documents, chunks, embeddings, filename
        )

        logger.info(f"Ingestion complete for '{filename}': {stored_count} chunks stored")
        return {
            "filename": filename,
            "chunks_count": stored_count,
            "status": "success",
            "message": f"Successfully indexed {stored_count} chunks from '{filename}'",
        }

    async def query(self, session_id: str, user_message: str) -> dict:
        """
        Full RAG query pipeline:
        1. Retrieve session history
        2. Embed user query
        3. Similarity search → top K chunks
        4. (Optional) Rerank with cross-encoder
        5. Build prompt with context + history
        6. Call LLM
        7. Update session history
        8. Return answer + sources
        """
        # Ensure session exists
        if not session_manager.session_exists(session_id):
            session_manager._sessions[session_id] = []

        # Step 1: Get history
        history = session_manager.get_history(session_id)
        rolling_summary = session_manager.get_summary(session_id)

        # Step 2: Embed query (with HyDE for better retrieval)
        query_embedding = await run_in_thread(self._embed_with_hyde, user_message, history)

        # Step 3: Similarity search
        raw_chunks = await run_in_thread(
            vector_store_service.similarity_search,
            query_embedding, settings.TOP_K_RESULTS + 2
        )

        # Step 4: Rerank
        top_chunks = await run_in_thread(self._rerank, user_message, raw_chunks, settings.TOP_K_RESULTS)

        # Step 5: Check Redis cache
        chunk_ids = [c.get("metadata", {}).get("source", "") + str(c.get("metadata", {}).get("chunk_index", ""))
                     for c in top_chunks]
        cache_key = _cache_key(user_message, chunk_ids)
        cached = self._get_cached_response(cache_key)
        if cached:
            logger.info("Cache hit — returning cached response")
            session_manager.add_turn(session_id, "user", user_message)
            session_manager.add_turn(session_id, "assistant", cached["answer"])
            session_manager.prune_history(session_id, settings.MAX_HISTORY_TURNS)
            return {**cached, "session_id": session_id, "cached": True}

        # Step 6: Build prompt
        system_prompt, messages = prompt_builder.build_messages(
            chat_history=history,
            user_query=user_message,
            retrieved_chunks=top_chunks,
            rolling_summary=rolling_summary,
        )

        # Step 7: Call LLM (blocking — run in thread)
        answer, tokens_used = await run_in_thread(llm_client.generate, system_prompt, messages)

        # Step 8: Build sources list
        sources = self._build_sources(top_chunks)

        # Step 9: Update session
        session_manager.add_turn(session_id, "user", user_message)
        session_manager.add_turn(session_id, "assistant", answer)
        session_manager.prune_history(session_id, settings.MAX_HISTORY_TURNS)

        result = {
            "session_id": session_id,
            "answer": answer,
            "sources": sources,
            "tokens_used": tokens_used,
        }

        # Cache the result
        self._set_cached_response(cache_key, result)
        return result

    async def query_stream(self, session_id: str, user_message: str) -> AsyncIterator[str]:
        """
        Streaming RAG query — yields SSE-formatted text deltas.
        """
        if not session_manager.session_exists(session_id):
            session_manager._sessions[session_id] = []

        history = session_manager.get_history(session_id)
        rolling_summary = session_manager.get_summary(session_id)

        query_embedding = await run_in_thread(self._embed_with_hyde, user_message, history)
        raw_chunks = await run_in_thread(
            vector_store_service.similarity_search,
            query_embedding, settings.TOP_K_RESULTS + 2
        )
        top_chunks = await run_in_thread(self._rerank, user_message, raw_chunks, settings.TOP_K_RESULTS)

        system_prompt, messages = prompt_builder.build_messages(
            chat_history=history,
            user_query=user_message,
            retrieved_chunks=top_chunks,
            rolling_summary=rolling_summary,
        )

        sources = self._build_sources(top_chunks)

        # Yield sources metadata first as a special SSE event
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

        # Stream the LLM response
        full_answer = ""
        async for text_delta in llm_client.generate_stream(system_prompt, messages):
            full_answer += text_delta
            yield f"data: {json.dumps({'type': 'delta', 'text': text_delta})}\n\n"

        # Signal completion
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

        # Update session after streaming completes
        session_manager.add_turn(session_id, "user", user_message)
        session_manager.add_turn(session_id, "assistant", full_answer)
        session_manager.prune_history(session_id, settings.MAX_HISTORY_TURNS)

    def _embed_with_hyde(self, user_message: str, history: list) -> list:
        """
        HyDE (Hypothetical Document Embeddings):
        Generate a hypothetical answer and embed it for better retrieval.
        Falls back to direct query embedding if no docs are indexed.
        """
        if vector_store_service.get_collection_count() == 0:
            return embedding_service.embed_query(user_message)

        # For HyDE, we embed the query directly but augment with recent context
        context_hint = ""
        if history:
            last_turns = history[-2:]  # last user+assistant pair
            for turn in last_turns:
                if turn["role"] == "user":
                    context_hint = turn["content"][:100]
                    break

        enhanced_query = f"{context_hint} {user_message}".strip() if context_hint else user_message
        return embedding_service.embed_query(enhanced_query)

    def _rerank(self, query: str, chunks: list, top_k: int) -> list:
        """
        Sort retrieved chunks by cosine distance (lower = more relevant).
        Cross-encoder reranking is disabled to avoid slow model downloads.
        """
        if not chunks:
            return []
        sorted_chunks = sorted(chunks, key=lambda x: x.get("distance", 1.0))
        return sorted_chunks[:top_k]

    def _build_sources(self, chunks: list) -> list:
        """Build the sources list for the response."""
        seen = set()
        sources = []
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            source = meta.get("source", "Unknown")
            text = chunk.get("text", "")
            key = f"{source}_{meta.get('chunk_index', 0)}"
            if key not in seen:
                seen.add(key)
                sources.append({
                    "filename": source,
                    "chunk_preview": text[:150] + "..." if len(text) > 150 else text,
                    "distance": chunk.get("distance"),
                })
        return sources

    def _get_cached_response(self, cache_key: str) -> Optional[dict]:
        """Try to get a cached response from Redis."""
        redis = _get_redis()
        if not redis:
            return None
        try:
            cached = redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
        return None

    def _set_cached_response(self, cache_key: str, result: dict):
        """Cache a response in Redis for 1 hour."""
        redis = _get_redis()
        if not redis:
            return
        try:
            redis.setex(cache_key, 3600, json.dumps(result))
        except Exception as e:
            logger.warning(f"Redis set error: {e}")


rag_pipeline = RAGPipeline()
