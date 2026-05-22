"""
Tests for RAG pipeline components: parser, chunker, vector store, and end-to-end flow.
"""
import pytest
from unittest.mock import patch, MagicMock


# ─── Document Parser Tests ────────────────────────────────────────────────────

class TestDocumentParser:
    def setup_method(self):
        from app.services.document_parser import DocumentParser
        self.parser = DocumentParser()

    def test_parse_txt_utf8(self):
        """Test parsing a UTF-8 encoded text file."""
        content = "Personal Loan FAQ\n\nQ: What is the rate?\nA: 10.5% p.a."
        result = self.parser.parse_txt(content.encode("utf-8"))
        assert "Personal Loan FAQ" in result
        assert "10.5%" in result

    def test_parse_txt_latin1(self):
        """Test parsing a Latin-1 encoded text file."""
        content = "Caf\xe9 banking services"
        result = self.parser.parse_txt(content.encode("latin-1"))
        assert len(result) > 0

    def test_parse_txt_empty_raises(self):
        """Test that empty text file raises HTTPException."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            self.parser.parse_txt(b"")
        assert exc_info.value.status_code == 400

    def test_parse_dispatcher_txt(self):
        """Test that parse() dispatches correctly for .txt files."""
        content = "Banking document content for testing purposes."
        result = self.parser.parse("test.txt", content.encode("utf-8"))
        assert "Banking document" in result

    def test_parse_unsupported_extension_raises(self):
        """Test that unsupported file extension raises HTTPException."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            self.parser.parse("file.xyz", b"some content")
        assert exc_info.value.status_code == 400
        assert "Unsupported file type" in exc_info.value.detail

    def test_parse_pdf_with_mock(self):
        """Test PDF parsing with mocked PyMuPDF."""
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Page 1 content about home loans."
        mock_doc = MagicMock()
        mock_doc.page_count = 1
        mock_doc.load_page.return_value = mock_page

        with patch("fitz.open", return_value=mock_doc):
            result = self.parser.parse_pdf(b"%PDF-1.4 fake content")
        assert "home loans" in result


# ─── Chunker Tests ────────────────────────────────────────────────────────────

class TestTextChunker:
    def setup_method(self):
        from app.services.chunker import TextChunker
        self.chunker = TextChunker()

    def test_chunk_returns_documents(self):
        """Test that chunking returns a list of Document objects."""
        text = "Banking FAQ\n\n" + ("Q: What is a loan?\nA: A loan is borrowed money.\n\n" * 30)
        chunks = self.chunker.chunk(text, "test.txt")
        assert len(chunks) > 0

    def test_chunk_metadata(self):
        """Test that each chunk has correct metadata."""
        text = "Sample banking text. " * 100
        chunks = self.chunker.chunk(text, "banking_faq.txt")
        for i, chunk in enumerate(chunks):
            assert chunk.metadata["source"] == "banking_faq.txt"
            assert "chunk_index" in chunk.metadata
            assert "char_count" in chunk.metadata

    def test_chunk_correct_count(self):
        """Test that chunking produces the expected number of chunks."""
        # ~2000 chars with chunk_size=500 should produce ~4+ chunks
        text = "A" * 2000
        chunks = self.chunker.chunk(text, "test.txt")
        assert len(chunks) >= 3

    def test_chunk_empty_text_returns_empty(self):
        """Test that empty text returns empty list."""
        chunks = self.chunker.chunk("", "empty.txt")
        assert chunks == []

    def test_chunk_whitespace_only_returns_empty(self):
        """Test that whitespace-only text returns empty list."""
        chunks = self.chunker.chunk("   \n\n   ", "whitespace.txt")
        assert chunks == []


# ─── Vector Store Tests ───────────────────────────────────────────────────────

class TestVectorStoreService:
    def setup_method(self):
        from app.services.vector_store import VectorStoreService
        self.service = VectorStoreService()

    def test_similarity_search_returns_top_k(self):
        """Test that similarity_search returns at most top_k results."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 10
        mock_collection.query.return_value = {
            "documents": [["chunk1", "chunk2", "chunk3"]],
            "metadatas": [[
                {"source": "doc1.txt", "chunk_index": 0, "page_hint": ""},
                {"source": "doc1.txt", "chunk_index": 1, "page_hint": ""},
                {"source": "doc2.txt", "chunk_index": 0, "page_hint": ""},
            ]],
            "distances": [[0.1, 0.2, 0.3]],
        }

        with patch("app.services.vector_store.get_chroma_collection", return_value=mock_collection):
            results = self.service.similarity_search([0.1] * 384, top_k=3)

        assert len(results) == 3
        assert results[0]["text"] == "chunk1"
        assert results[0]["distance"] == 0.1

    def test_similarity_search_empty_collection(self):
        """Test similarity_search on empty collection returns empty list."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0

        with patch("app.services.vector_store.get_chroma_collection", return_value=mock_collection):
            results = self.service.similarity_search([0.1] * 384, top_k=5)

        assert results == []

    def test_list_sources(self):
        """Test list_sources returns unique source names."""
        mock_collection = MagicMock()
        mock_collection.count.return_value = 3
        mock_collection.get.return_value = {
            "metadatas": [
                {"source": "doc1.txt"},
                {"source": "doc2.txt"},
                {"source": "doc1.txt"},  # duplicate
            ]
        }

        with patch("app.services.vector_store.get_chroma_collection", return_value=mock_collection):
            sources = self.service.list_sources()

        assert len(sources) == 2
        assert "doc1.txt" in sources
        assert "doc2.txt" in sources


# ─── End-to-End RAG Pipeline Test ─────────────────────────────────────────────

class TestRAGPipelineE2E:
    @pytest.mark.asyncio
    async def test_ingest_and_query(self):
        """End-to-end test: ingest a document then query it."""
        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1] * 384] * 10

        mock_collection = MagicMock()
        mock_collection.count.return_value = 5
        mock_collection.upsert.return_value = None
        mock_collection.query.return_value = {
            "documents": [["Personal loan interest rates range from 10.5% to 24% p.a."]],
            "metadatas": [[{"source": "loans.txt", "chunk_index": 0, "page_hint": ""}]],
            "distances": [[0.1]],
        }

        mock_response = MagicMock()
        mock_response.text = "Interest rates are 10.5% to 24% p.a."
        mock_response.usage_metadata = MagicMock()
        mock_response.usage_metadata.prompt_token_count = 100
        mock_response.usage_metadata.candidates_token_count = 30
        mock_gemini = MagicMock()
        mock_gemini.generate_content.return_value = mock_response

        with patch("app.services.embeddings._embedding_model", mock_model), \
             patch("app.services.vector_store._collection", mock_collection), \
             patch("app.services.llm_client._gemini_model", mock_gemini):

            from app.services.rag_pipeline import RAGPipeline
            pipeline = RAGPipeline()

            # Ingest
            doc_content = "Personal Loan FAQ\n\n" + ("Q: Rate?\nA: 10.5% to 24% p.a.\n\n" * 20)
            ingest_result = await pipeline.ingest_document("loans.txt", doc_content.encode())
            assert ingest_result["status"] == "success"
            assert ingest_result["chunks_count"] > 0

            # Query
            query_result = await pipeline.query("test-session", "What is the interest rate?")
            assert "answer" in query_result
            assert "sources" in query_result
            assert "session_id" in query_result
            assert len(query_result["answer"]) > 0
