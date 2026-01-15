"""Text chunking service for document processing."""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import tiktoken


class ChunkingService:
    """Service for chunking text documents."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        """
        Initialize the chunking service.
        
        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self._token_length,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def _token_length(self, text: str) -> int:
        """Calculate token length of text."""
        return len(self.tokenizer.encode(text))
    
    def chunk_text(
        self, 
        text: str, 
        title: str = None, 
        source: str = None
    ) -> List[Dict]:
        """
        Chunk text into smaller pieces with metadata.
        
        Args:
            text: Text to chunk
            title: Optional document title
            source: Optional document source
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Add metadata to each chunk
        chunk_dicts = []
        for idx, chunk in enumerate(chunks):
            chunk_dict = {
                "text": chunk,
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "title": title,
                "source": source,
                "token_count": self._token_length(chunk)
            }
            chunk_dicts.append(chunk_dict)
        
        return chunk_dicts
    
    def get_chunking_stats(self, chunks: List[Dict]) -> Dict:
        """Get statistics about chunking results."""
        if not chunks:
            return {}
        
        token_counts = [c["token_count"] for c in chunks]
        
        return {
            "total_chunks": len(chunks),
            "avg_tokens_per_chunk": sum(token_counts) / len(token_counts),
            "min_tokens": min(token_counts),
            "max_tokens": max(token_counts),
            "total_tokens": sum(token_counts)
        }
