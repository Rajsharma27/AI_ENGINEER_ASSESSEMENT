"""Embedding generation service using Cohere."""
import cohere
from typing import List
import numpy as np


class EmbeddingService:
    """Service for generating embeddings using Cohere."""
    
    def __init__(self, api_key: str, model: str = "embed-english-v3.0"):
        """
        Initialize the embedding service.
        
        Args:
            api_key: Cohere API key
            model: Embedding model name
        """
        self.client = cohere.ClientV2(api_key)
        self.model = model
        self.dimension = 1024  # Cohere embed-english-v3.0 dimension
    
    def embed_texts(self, texts: List[str], input_type: str = "search_document") -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            input_type: Type of input ("search_document" for indexing, "search_query" for queries)
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Cohere API accepts input_type parameter
        response = self.client.embed(
            texts=texts,
            model=self.model,
            input_type=input_type,
            embedding_types=["float"]
        )
        
        return response.embeddings.float_
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.
        
        Args:
            query: Query string
            
        Returns:
            Embedding vector
        """
        embeddings = self.embed_texts([query], input_type="search_query")
        return embeddings[0] if embeddings else []
    
    def embed_document(self, text: str) -> List[float]:
        """
        Generate embedding for a single document.
        
        Args:
            text: Document text
            
        Returns:
            Embedding vector
        """
        embeddings = self.embed_texts([text], input_type="search_document")
        return embeddings[0] if embeddings else []
    
    def batch_embed_documents(self, texts: List[str], batch_size: int = 96) -> List[List[float]]:
        """
        Embed documents in batches for efficiency.
        
        Args:
            texts: List of document texts
            batch_size: Maximum batch size (Cohere limit is 96)
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.embed_texts(batch, input_type="search_document")
            all_embeddings.extend(embeddings)
        
        return all_embeddings
