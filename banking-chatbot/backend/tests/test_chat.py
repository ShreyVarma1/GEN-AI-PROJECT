"""
Tests for the /chat endpoint.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def _make_gemini_mock(answer: str = "Personal loan interest rates range from 10.5% to 24% p.a."):
    """Build a mock Gemini GenerativeModel that returns a canned answer."""
    mock_response = MagicMock()
    mock_response.text = answer
    mock_response.usage_metadata = MagicMock()
    mock_response.usage_metadata.prompt_token_count = 150
    mock_response.usage_metadata.candidates_token_count = 50
    mock_gemini = MagicMock()
    mock_gemini.generate_content.return_value = mock_response
    return mock_gemini


@pytest.fixture
def client():
    """Create a test client with mocked dependencies."""
    mock_embed_model = MagicMock()
    mock_embed_model.encode.return_value = [[0.1] * 384]

    mock_collection = MagicMock()
    mock_collection.count.return_value = 10
    mock_collection.query.return_value = {
        "documents": [["Sample banking document text about personal loans."]],
        "metadatas": [[{"source": "personal_loans_faq.txt", "chunk_index": 0, "page_hint": ""}]],
        "distances": [[0.15]],
    }

    mock_gemini = _make_gemini_mock()

    with patch("app.services.embeddings._embedding_model", mock_embed_model), \
         patch("app.services.vector_store._collection", mock_collection), \
         patch("app.services.llm_client._gemini_model", mock_gemini):

        from app.main import app
        with TestClient(app) as c:
            yield c


def test_chat_with_valid_message(client):
    """Test POST /chat with a valid message returns answer and sources."""
    response = client.post("/api/v1/chat", json={"message": "What is the interest rate on personal loans?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "session_id" in data
    assert "sources" in data
    assert len(data["answer"]) > 0
    assert data["session_id"] is not None


def test_chat_auto_creates_session(client):
    """Test POST /chat without session_id auto-creates one."""
    response = client.post("/api/v1/chat", json={"message": "Tell me about credit cards."})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["session_id"] is not None
    assert len(data["session_id"]) > 0


def test_chat_with_provided_session_id(client):
    """Test POST /chat with an explicit session_id uses that session."""
    session_id = "test-session-12345"
    response = client.post("/api/v1/chat", json={
        "message": "What documents do I need for a home loan?",
        "session_id": session_id,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id


def test_chat_multi_turn_context(client):
    """Test multi-turn conversation maintains context."""
    session_id = "multi-turn-test-session"

    r1 = client.post("/api/v1/chat", json={
        "message": "Tell me about personal loans.",
        "session_id": session_id,
    })
    assert r1.status_code == 200

    r2 = client.post("/api/v1/chat", json={
        "message": "What is the interest rate for it?",
        "session_id": session_id,
    })
    assert r2.status_code == 200
    data = r2.json()
    assert "answer" in data
    assert data["session_id"] == session_id


def test_chat_empty_message_returns_422(client):
    """Test POST /chat with empty message returns 422 validation error."""
    response = client.post("/api/v1/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_whitespace_message_returns_422(client):
    """Test POST /chat with whitespace-only message returns 422."""
    response = client.post("/api/v1/chat", json={"message": "   "})
    assert response.status_code == 422


def test_chat_message_too_long_returns_422(client):
    """Test POST /chat with message exceeding 2000 chars returns 422."""
    long_message = "a" * 2001
    response = client.post("/api/v1/chat", json={"message": long_message})
    assert response.status_code == 422


def test_chat_sources_structure(client):
    """Test that sources in response have correct structure."""
    response = client.post("/api/v1/chat", json={"message": "What are NEFT limits?"})
    assert response.status_code == 200
    data = response.json()
    for source in data.get("sources", []):
        assert "filename" in source
        assert "chunk_preview" in source


def test_clear_session(client):
    """Test DELETE /chat/{session_id} clears the session."""
    r1 = client.post("/api/v1/chat", json={"message": "Hello"})
    session_id = r1.json()["session_id"]
    r2 = client.delete(f"/api/v1/chat/{session_id}")
    assert r2.status_code == 200
    assert "cleared" in r2.json()["message"].lower()


def test_clear_nonexistent_session_returns_404(client):
    """Test clearing a non-existent session returns 404."""
    response = client.delete("/api/v1/chat/nonexistent-session-id")
    assert response.status_code == 404
