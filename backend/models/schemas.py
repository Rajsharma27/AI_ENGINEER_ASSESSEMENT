"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional


class IngestRequest(BaseModel):
    """Request model for document ingestion."""
    text: str = Field(..., description="Text content to ingest")
    title: Optional[str] = Field(None, description="Document title")
    source: Optional[str] = Field(None, description="Document source")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is a sample document about artificial intelligence...",
                "title": "Introduction to AI",
                "source": "AI Textbook Chapter 1"
            }
        }


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    message: str
    chunks_created: int
    document_id: str


class QueryRequest(BaseModel):
    """Request model for querying the RAG system."""
    query: str = Field(..., description="User question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is artificial intelligence?"
            }
        }


class SourceChunk(BaseModel):
    """Model for a source chunk with metadata."""
    text: str
    source: Optional[str] = None
    title: Optional[str] = None
    chunk_index: int
    score: float


class QueryResponse(BaseModel):
    """Response model for RAG query."""
    answer: str
    sources: List[SourceChunk]
    timing: dict
    cost_estimate: dict
    has_answer: bool = True


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    qdrant_connected: bool
    collection_exists: bool
    document_count: int
