"""Retrieval service with MMR (Maximal Marginal Relevance)."""
import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity


class RetrieverService:
    """Service for retrieving relevant documents with MMR."""
    
    def __init__(self, vector_store, embedding_service):
        """
        Initialize the retriever service.
        
        Args:
            vector_store: VectorStoreService instance
            embedding_service: EmbeddingService instance
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 10,
        use_mmr: bool = True,
        lambda_param: float = 0.5
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User query
            top_k: Number of results to retrieve
            use_mmr: Whether to apply MMR for diversity
            lambda_param: MMR lambda parameter (0=diversity, 1=relevance)
            
        Returns:
            List of retrieved documents
        """
        # Generate query embedding
        query_vector = self.embedding_service.embed_query(query)
        
        # Search vector store
        results = self.vector_store.search(query_vector, top_k=top_k * 2 if use_mmr else top_k)
        
        if not results:
            return []
        
        # Apply MMR if requested
        if use_mmr and len(results) > top_k:
            results = self._apply_mmr(
                query_vector=query_vector,
                candidates=results,
                top_k=top_k,
                lambda_param=lambda_param
            )
        else:
            results = results[:top_k]
        
        return results
    
    def _apply_mmr(
        self, 
        query_vector: List[float], 
        candidates: List[Dict], 
        top_k: int,
        lambda_param: float = 0.5
    ) -> List[Dict]:
        """
        Apply Maximal Marginal Relevance to diversify results.
        
        Args:
            query_vector: Query embedding
            candidates: Candidate documents
            top_k: Number of results to select
            lambda_param: Trade-off between relevance and diversity
            
        Returns:
            Diversified list of documents
        """
        if len(candidates) <= top_k:
            return candidates
        
        # Get embeddings for all candidates
        candidate_texts = [c["text"] for c in candidates]
        candidate_embeddings = self.embedding_service.embed_texts(
            candidate_texts, 
            input_type="search_document"
        )
        
        # Convert to numpy arrays
        query_vec = np.array(query_vector).reshape(1, -1)
        candidate_vecs = np.array(candidate_embeddings)
        
        # Calculate relevance scores (similarity to query)
        relevance_scores = cosine_similarity(query_vec, candidate_vecs)[0]
        
        # MMR algorithm
        selected_indices = []
        remaining_indices = list(range(len(candidates)))
        
        # Select first document (highest relevance)
        first_idx = np.argmax(relevance_scores)
        selected_indices.append(first_idx)
        remaining_indices.remove(first_idx)
        
        # Iteratively select documents
        while len(selected_indices) < top_k and remaining_indices:
            selected_vecs = candidate_vecs[selected_indices]
            
            mmr_scores = []
            for idx in remaining_indices:
                # Relevance to query
                relevance = relevance_scores[idx]
                
                # Maximum similarity to already selected documents
                candidate_vec = candidate_vecs[idx].reshape(1, -1)
                similarities = cosine_similarity(candidate_vec, selected_vecs)[0]
                max_similarity = np.max(similarities)
                
                # MMR score
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_similarity
                mmr_scores.append(mmr_score)
            
            # Select document with highest MMR score
            best_idx = remaining_indices[np.argmax(mmr_scores)]
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)
        
        # Return selected documents in order
        return [candidates[idx] for idx in selected_indices]
