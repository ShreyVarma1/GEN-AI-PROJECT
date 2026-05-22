"""
Tests for the /upload endpoint and /health endpoint.
"""
import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked dependencies."""
    mock_embed_model = MagicMock()
    mock_embed_model.encode.return_value = [[0.1] * 384, [0.2] * 384]

    mock_collection = MagicMock()
    mock_collection.count.return_value = 5
    mock_collection.upsert.return_value = None
    mock_collection.get.return_value = {
        "ids": [],
        "metadatas": [{"source": "test.txt"}],
    }

    mock_gemini = MagicMock()

    with patch("app.services.embeddings._embedding_model", mock_embed_model), \
         patch("app.services.vector_store._collection", mock_collection), \
         patch("app.services.llm_client._gemini_model", mock_gemini):

        from app.main import app
        with TestClient(app) as c:
            yield c


def _make_txt_file(content: str = "This is a test banking document about personal loans.") -> bytes:
    return content.encode("utf-8")


def test_upload_valid_txt(client):
    """Test POST /upload with a valid TXT file returns 200 and chunks_indexed > 0."""
    content = _make_txt_file(
        "Personal Loan FAQ\n\n" + "Q: What is the interest rate?\nA: 10.5% to 24% p.a.\n\n" * 20
    )
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test_loans.txt", io.BytesIO(content), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_loans.txt"
    assert data["chunks_indexed"] >= 0
    assert data["status"] in ("success", "warning")


def test_upload_invalid_file_type(client):
    """Test POST /upload with an invalid file type returns 400."""
    response = client.post(
        "/api/v1/upload",
        files={"file": ("malware.exe", io.BytesIO(b"MZ\x90\x00"), "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_invalid_file_type_js(client):
    """Test POST /upload with .js file returns 400."""
    response = client.post(
        "/api/v1/upload",
        files={"file": ("script.js", io.BytesIO(b"console.log('hello')"), "text/javascript")},
    )
    assert response.status_code == 400


def test_upload_empty_file(client):
    """Test POST /upload with an empty file returns 400."""
    response = client.post(
        "/api/v1/upload",
        files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")},
    )
    assert response.status_code == 400


def test_upload_oversized_file(client):
    """Test POST /upload with a file exceeding 10MB returns 400."""
    large_content = b"x" * (11 * 1024 * 1024)  # 11 MB
    response = client.post(
        "/api/v1/upload",
        files={"file": ("large.txt", io.BytesIO(large_content), "text/plain")},
    )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()


def test_upload_response_structure(client):
    """Test that upload response has the correct structure."""
    content = _make_txt_file("Banking FAQ content " * 50)
    response = client.post(
        "/api/v1/upload",
        files={"file": ("banking_faq.txt", io.BytesIO(content), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "chunks_indexed" in data
    assert "status" in data
    assert "message" in data


def test_health_endpoint(client):
    """Test GET /health returns 200 with status ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "vector_db" in data
    assert "documents_indexed" in data
    assert "timestamp" in data


def test_health_returns_sources_list(client):
    """Test GET /health returns a list of indexed sources."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert isinstance(data["sources"], list)
