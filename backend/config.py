"""Configuration management for the RAG application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "rag_documents"
    
    # Cohere Configuration
    cohere_api_key: str
    
    # Groq Configuration
    groq_api_key: str
    
    # Optional: OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # Embedding Configuration
    embedding_model: str = "embed-english-v3.0"
    embedding_dimension: int = 1024
    
    # Chunking Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 100
    
    # Retrieval Configuration
    top_k: int = 10
    rerank_top_n: int = 5
    
    # LLM Configuration
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
