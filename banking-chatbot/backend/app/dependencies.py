"""
Shared dependency injection for FastAPI.
Provides singleton instances of core services.
"""
from app.services.vector_store import vector_store_service, get_chroma_collection
from app.services.embeddings import embedding_service, get_embedding_model
from app.services.llm_client import llm_client
from app.services.rag_pipeline import rag_pipeline
from app.utils.session_manager import session_manager


def get_vector_store():
    return vector_store_service


def get_embedding_service():
    return embedding_service


def get_llm_client():
    return llm_client


def get_rag_pipeline():
    return rag_pipeline


def get_session_manager():
    return session_manager
