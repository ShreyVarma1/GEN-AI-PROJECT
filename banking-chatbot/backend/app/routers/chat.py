import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest, ChatResponse, SourceChunk
from app.services.rag_pipeline import rag_pipeline
from app.utils.session_manager import session_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the banking chatbot.
    - If session_id is not provided, a new session is created automatically.
    - If stream=True, returns a Server-Sent Events stream.
    """
    # Auto-create session if not provided
    session_id = request.session_id
    if not session_id:
        session_id = session_manager.new_session()
        logger.info(f"Auto-created session: {session_id}")
    elif not session_manager.session_exists(session_id):
        # Initialize the session if it's a new ID from the client
        session_manager._sessions[session_id] = []

    # Streaming response
    if request.stream:
        async def event_generator():
            try:
                async for chunk in rag_pipeline.query_stream(session_id, request.message):
                    yield chunk
            except HTTPException as e:
                import json
                yield f"data: {json.dumps({'type': 'error', 'message': e.detail})}\n\n"
            except Exception as e:
                import json
                logger.error(f"Streaming error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': 'An unexpected error occurred.'})}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "X-Session-Id": session_id,
            },
        )

    # Standard JSON response
    result = await rag_pipeline.query(session_id, request.message)

    sources = [
        SourceChunk(
            filename=s["filename"],
            chunk_preview=s["chunk_preview"],
            distance=s.get("distance"),
        )
        for s in result.get("sources", [])
    ]

    return ChatResponse(
        session_id=result["session_id"],
        answer=result["answer"],
        sources=sources,
        tokens_used=result.get("tokens_used"),
    )


@router.delete("/chat/{session_id}")
async def clear_session(session_id: str):
    """Clear the chat history for a given session."""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    session_manager.clear_session(session_id)
    return {"message": f"Session '{session_id}' cleared successfully."}
