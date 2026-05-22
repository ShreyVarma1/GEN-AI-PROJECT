import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings

logger = logging.getLogger(__name__)


class LangChainDocument:
    """Lightweight Document object compatible with LangChain Document interface."""
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(source={self.metadata.get('source')}, chunk={self.metadata.get('chunk_index')})"


class TextChunker:
    """Splits documents into overlapping chunks with metadata."""

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk(self, text: str, source_filename: str) -> List[LangChainDocument]:
        """Split text into chunks and attach metadata."""
        if not text or not text.strip():
            logger.warning(f"Empty text provided for chunking: {source_filename}")
            return []

        raw_chunks = self.splitter.split_text(text)
        documents = []
        for idx, chunk_text in enumerate(raw_chunks):
            if not chunk_text.strip():
                continue
            # Derive a page hint from content if possible
            page_hint = ""
            if "[Page " in chunk_text:
                try:
                    page_hint = chunk_text.split("[Page ")[1].split("]")[0]
                except Exception:
                    pass

            doc = LangChainDocument(
                page_content=chunk_text.strip(),
                metadata={
                    "source": source_filename,
                    "chunk_index": idx,
                    "page_hint": page_hint,
                    "char_count": len(chunk_text),
                }
            )
            documents.append(doc)

        logger.info(f"Chunked '{source_filename}' into {len(documents)} chunks")
        return documents


text_chunker = TextChunker()
