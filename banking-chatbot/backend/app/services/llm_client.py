import asyncio
import logging
import concurrent.futures
from typing import List, AsyncIterator
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

_gemini_client = None
_gemini_model = None


def get_gemini_model():
    """Singleton Gemini GenerativeModel. Re-initializes if model name changes."""
    global _gemini_client, _gemini_model
    # Newer models (gemini-2.5-x) require the "models/" prefix.
    # Older SDK behaviour stripped it — we now always ensure it's present.
    model_name = settings.LLM_MODEL
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"

    # Re-create if model name changed (e.g. after .env reload)
    if _gemini_model is None or getattr(_gemini_model, "_model_name", None) != model_name:
        import google.generativeai as genai
        if not settings.GOOGLE_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY is not configured. Please set it in your .env file."
            )
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        _gemini_model = genai.GenerativeModel(model_name=model_name)
        _gemini_model._model_name = model_name  # track for change detection
        logger.info(f"Gemini model loaded: {model_name}")
    return _gemini_model


def _build_gemini_contents(system_prompt: str, messages: List[dict]) -> list:
    """
    Convert OpenAI-style messages + system prompt into Gemini's content format.

    Gemini uses:
      - contents: list of {"role": "user"|"model", "parts": [{"text": "..."}]}
      - system_instruction is passed separately to GenerativeModel or prepended

    We prepend the system prompt as the first user turn (acknowledged by model)
    so it works with the basic GenerativeModel API without needing system_instruction
    (which requires a newer SDK version).
    """
    contents = []

    # Inject system prompt as a priming exchange
    contents.append({
        "role": "user",
        "parts": [{"text": f"[System Instructions]\n{system_prompt}"}]
    })
    contents.append({
        "role": "model",
        "parts": [{"text": "Understood. I will follow these instructions strictly."}]
    })

    # Convert the rest of the messages
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    return contents


class LLMClient:
    """Wraps the Google Gemini API for chat completions."""

    def generate(
        self,
        system_prompt: str,
        messages: List[dict],
        max_tokens: int = 1024,
    ) -> tuple[str, int]:
        """
        Generate a response from Gemini.
        Returns (response_text, tokens_used).
        Runs synchronously — call via run_in_executor from async context.
        """
        import google.generativeai as genai
        from google.generativeai import types as genai_types

        model = get_gemini_model()
        contents = _build_gemini_contents(system_prompt, messages)

        generation_config = genai_types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=0.3,   # lower = more factual/grounded
        )

        try:
            response = model.generate_content(
                contents,
                generation_config=generation_config,
            )
            text = response.text if response.text else ""

            # Token usage (Gemini provides usage_metadata)
            tokens_used = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                tokens_used = (
                    getattr(response.usage_metadata, "prompt_token_count", 0) +
                    getattr(response.usage_metadata, "candidates_token_count", 0)
                )

            logger.info(
                f"Gemini call complete. Model: {settings.LLM_MODEL}, "
                f"Tokens used: {tokens_used}"
            )
            return text, tokens_used

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini API error: {error_msg}")
            if "api_key" in error_msg.lower() or "api key" in error_msg.lower() or "invalid" in error_msg.lower():
                raise HTTPException(status_code=401, detail="Invalid Google API key.")
            elif "quota" in error_msg.lower() or "429" in error_msg or "ResourceExhausted" in error_msg:
                raise HTTPException(status_code=429, detail="Gemini rate limit / quota exceeded. Please try again shortly.")
            elif "blocked" in error_msg.lower() or "safety" in error_msg.lower():
                raise HTTPException(status_code=400, detail="Response blocked by Gemini safety filters.")
            elif "model name format" in error_msg.lower() or "not found" in error_msg.lower():
                raise HTTPException(status_code=500, detail=f"Gemini model not available: {settings.LLM_MODEL}. Check LLM_MODEL in .env.")
            else:
                raise HTTPException(status_code=500, detail=f"LLM generation failed: {error_msg}")

    async def generate_stream(
        self,
        system_prompt: str,
        messages: List[dict],
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """
        Stream response from Gemini as text deltas.
        Runs the blocking stream in a thread pool to avoid blocking the event loop.
        Yields text chunks as they arrive.
        """
        import google.generativeai as genai
        from google.generativeai import types as genai_types

        model = get_gemini_model()
        contents = _build_gemini_contents(system_prompt, messages)
        generation_config = genai_types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=0.3,
        )

        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def _stream_worker():
            try:
                response = model.generate_content(
                    contents,
                    generation_config=generation_config,
                    stream=True,
                )
                for chunk in response:
                    try:
                        text = chunk.text
                        if text:
                            loop.call_soon_threadsafe(queue.put_nowait, text)
                    except Exception:
                        pass  # skip empty/blocked chunks
            except Exception as e:
                loop.call_soon_threadsafe(queue.put_nowait, Exception(f"ERR:{e}"))
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = loop.run_in_executor(executor, _stream_worker)

        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                if isinstance(item, Exception):
                    msg = str(item)
                    raise HTTPException(status_code=500, detail=f"Gemini streaming failed: {msg[4:]}")
                yield item
        finally:
            await future
            executor.shutdown(wait=False)


llm_client = LLMClient()
