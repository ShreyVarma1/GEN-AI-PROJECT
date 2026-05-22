from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM Configuration — Google Gemini
    GOOGLE_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.0-flash"   # fast & free-tier friendly; swap to gemini-2.5-flash for higher quality

    # Embedding Configuration
    EMBEDDING_MODEL: str = "models/text-embedding-004"

    # ChromaDB Configuration
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "banking_docs"

    # Chunking Configuration
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # RAG Configuration
    TOP_K_RESULTS: int = 5
    MAX_HISTORY_TURNS: int = 10

    # Redis (optional caching)
    REDIS_URL: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def get_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


def get_settings() -> Settings:
    return Settings()


settings = get_settings()

