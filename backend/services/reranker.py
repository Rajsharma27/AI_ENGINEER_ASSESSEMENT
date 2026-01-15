"""Reranking service using Cohere Rerank."""
import cohere
from typing import List, Dict


class RerankerService:
    """Service for reranking documents using Cohere."""
    
    def __init__(self, api_key: str, model: str = "rerank-english-v3.0"):
        """
        Initialize the reranker service.
        
        Args:
            api_key: Cohere API key
            model: Rerank model name
        """
        self.client = cohere.ClientV2(api_key)
        self.model = model
    
    def rerank(
        self, 
        query: str, 
        documents: List[Dict], 
        top_n: int = 5
    ) -> List[Dict]:
        """
        Rerank documents based on relevance to query.
        
        Args:
            query: User query
            documents: List of document dictionaries with 'text' field
            top_n: Number of top documents to return
            
        Returns:
            Reranked list of documents with updated scores
        """
        if not documents:
            return []
        
        # Extract texts for reranking
        texts = [doc["text"] for doc in documents]
        
        # Call Cohere rerank API
        try:
            response = self.client.rerank(
                query=query,
                documents=texts,
                top_n=min(top_n, len(documents)),
                model=self.model
            )
            
            # Map reranked results back to original documents
            reranked_docs = []
            for result in response.results:
                original_doc = documents[result.index].copy()
                original_doc["rerank_score"] = result.relevance_score
                original_doc["original_rank"] = result.index
                reranked_docs.append(original_doc)
            
            return reranked_docs
            
        except Exception as e:
            # If reranking fails, return original top_n documents
            print(f"Reranking failed: {e}")
            return documents[:top_n]
    
    def rerank_with_metadata(
        self, 
        query: str, 
        documents: List[Dict], 
        top_n: int = 5
    ) -> Dict:
        """
        Rerank documents and return with metadata.
        
        Args:
            query: User query
            documents: List of document dictionaries
            top_n: Number of top documents to return
            
        Returns:
            Dictionary with reranked documents and metadata
        """
        reranked_docs = self.rerank(query, documents, top_n)
        
        return {
            "documents": reranked_docs,
            "original_count": len(documents),
            "reranked_count": len(reranked_docs),
            "model": self.model
        }
