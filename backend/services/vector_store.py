"""Vector store service using Qdrant."""
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, 
    VectorParams, 
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
from typing import List, Dict, Optional
import uuid


class VectorStoreService:
    """Service for managing vector storage in Qdrant."""
    
    def __init__(
        self, 
        url: str, 
        api_key: str, 
        collection_name: str,
        dimension: int = 1024
    ):
        """
        Initialize the vector store service.
        
        Args:
            url: Qdrant instance URL
            api_key: Qdrant API key
            collection_name: Name of the collection
            dimension: Vector dimension
        """
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        self.dimension = dimension
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure collection exists, create if it doesn't."""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.dimension,
                    distance=Distance.COSINE
                )
            )
    
    def add_documents(
        self, 
        texts: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict]
    ) -> str:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            
        Returns:
            Document ID (shared across all chunks)
        """
        document_id = str(uuid.uuid4())
        
        points = []
        for idx, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
            point_id = str(uuid.uuid4())
            
            payload = {
                "text": text,
                "document_id": document_id,
                "chunk_index": metadata.get("chunk_index", idx),
                "title": metadata.get("title"),
                "source": metadata.get("source"),
                "token_count": metadata.get("token_count", 0)
            }
            
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            )
        
        # Upload points to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return document_id
    
    def search(
        self, 
        query_vector: List[float], 
        top_k: int = 10,
        document_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            document_id: Optional filter by document ID
            
        Returns:
            List of search results with text and metadata
        """
        query_filter = None
        if document_id:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=query_filter
        ).points
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text", ""),
                "document_id": result.payload.get("document_id"),
                "chunk_index": result.payload.get("chunk_index", 0),
                "title": result.payload.get("title"),
                "source": result.payload.get("source"),
                "token_count": result.payload.get("token_count", 0)
            })
        
        return formatted_results
    
    def get_collection_info(self) -> Dict:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "exists": True,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count
            }
        except Exception as e:
            return {
                "exists": False,
                "error": str(e)
            }
    
    def delete_collection(self):
        """Delete the entire collection."""
        self.client.delete_collection(self.collection_name)
