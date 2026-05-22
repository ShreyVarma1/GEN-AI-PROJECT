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

# Single worker — Google API calls are I/O bound, not CPU bound
_executor = ThreadPoolExecutor(max_workers=2)

logger = logging.getLogger(__name__)

# Optional Redis cache
_redis_client = None


async def run_in_thread(func, *args):
    """Run a blocking function in a thread pool executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, func, *args)


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
            _redis_client = False
    return _redis_client if _redis_client else None


def _cache_key(query: str, chunk_ids: list) -> str:
    payload = query.lower().strip() + "|" + ",".join(sorted(chunk_ids))
    return "rag:" + hashlib.sha256(payload.encode()).hexdigest()


class RAGPipeline:

    async def ingest_document(self, filename: str, file_bytes: bytes) -> dict:
        logger.info(f"Starting ingestion for: {filename}")

        raw_text = await run_in_thread(document_parser.parse, filename, file_bytes)
        logger.info(f"Parsed '{filename}': {len(raw_text)} characters")

        chunks = await run_in_thread(text_chunker.chunk, raw_text, filename)
        if not chunks:
            return {"filename": filename, "chunks_count": 0, "status": "warning",
                    "message": "Document parsed but produced no chunks."}

        texts = [chunk.page_content for chunk in chunks]
        # Run embedding in thread (blocking HTTP calls)
        embeddings = await run_in_thread(embedding_service.embed_texts, texts)

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
        if not session_manager.session_exists(session_id):
            session_manager._sessions[session_id] = []

        history = session_manager.get_history(session_id)
        rolling_summary = session_manager.get_summary(session_id)

        # Embed query
        query_embedding = await run_in_thread(
            embedding_service.embed_query, user_message
        )

        # Similarity search
        raw_chunks = await run_in_thread(
            vector_store_service.similarity_search,
            query_embedding, settings.TOP_K_RESULTS + 2
        )

        top_chunks = self._rerank(user_message, raw_chunks, settings.TOP_K_RESULTS)

        # Redis cache check
        chunk_ids = [
            c.get("metadata", {}).get("source", "") + str(c.get("metadata", {}).get("chunk_index", ""))
            for c in top_chunks
        ]
        cache_key = _cache_key(user_message, chunk_ids)
        cached = self._get_cached_response(cache_key)
        if cached:
            logger.info("Cache hit — returning cached response")
            session_manager.add_turn(session_id, "user", user_message)
            session_manager.add_turn(session_id, "assistant", cached["answer"])
            session_manager.prune_history(session_id, settings.MAX_HISTORY_TURNS)
            return {**cached, "session_id": session_id, "cached": True}

        system_prompt, messages = prompt_builder.build_messages(
            chat_history=history,
            user_query=user_message,
            retrieved_chunks=top_chunks,
            rolling_summary=rolling_summary,
        )

        answer, tokens_used = await run_in_thread(llm_client.generate, system_prompt, messages)

        sources = self._build_sources(top_chunks)

        session_manager.add_turn(session_id, "user", user_message)
        session_manager.add_turn(session_id, "assistant", answer)
        session_manager.prune_history(session_id, settings.MAX_HISTORY_TURNS)

        result = {
            "session_id": session_id,
            "answer": answer,
            "sources": sources,
            "tokens_used": tokens_used,
        }
        self._set_cached_response(cache_key, result)
        return result

    async def query_stream(self, session_id: str, user_message: str) -> AsyncIterator[str]:
        """Streaming RAG — yields SSE events."""
        if not session_manager.session_exists(session_id):
            session_manager._sessions[session_id] = []

        history = session_manager.get_history(session_id)
        rolling_summary = session_manager.get_summary(session_id)

        query_embedding = await run_in_thread(embedding_service.embed_query, user_message)
        raw_chunks = await run_in_thread(
            vector_store_service.similarity_search,
            query_embedding, settings.TOP_K_RESULTS + 2
        )
        top_chunks = self._rerank(user_message, raw_chunks, settings.TOP_K_RESULTS)

        system_prompt, messages = prompt_builder.build_messages(
            chat_history=history,
            user_query=user_message,
            retrieved_chunks=top_chunks,
            rolling_summary=rolling_summary,
        )

        sources = self._build_sources(top_chunks)
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

        full_answer = ""
        async for text_delta in llm_client.generate_stream(system_prompt, messages):
            full_answer += text_delta
            yield f"data: {json.dumps({'type': 'delta', 'text': text_delta})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

        session_manager.add_turn(session_id, "user", user_message)
        session_manager.add_turn(session_id, "assistant", full_answer)
        session_manager.prune_history(session_id, settings.MAX_HISTORY_TURNS)

    def _rerank(self, query: str, chunks: list, top_k: int) -> list:
        if not chunks:
            return []
        return sorted(chunks, key=lambda x: x.get("distance", 1.0))[:top_k]

    def _build_sources(self, chunks: list) -> list:
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
        redis = _get_redis()
        if not redis:
            return
        try:
            redis.setex(cache_key, 3600, json.dumps(result))
        except Exception as e:
            logger.warning(f"Redis set error: {e}")


rag_pipeline = RAGPipeline()
