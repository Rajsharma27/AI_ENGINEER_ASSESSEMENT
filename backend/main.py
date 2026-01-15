"""FastAPI main application for Mini RAG system."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import tiktoken

from config import settings
from models.schemas import (
    IngestRequest, 
    IngestResponse, 
    QueryRequest, 
    QueryResponse,
    SourceChunk,
    HealthResponse
)
from services.chunking import ChunkingService
from services.embeddings import EmbeddingService
from services.vector_store import VectorStoreService
from services.retriever import RetrieverService
from services.reranker import RerankerService
from services.llm import LLMService


# Global service instances
chunking_service = None
embedding_service = None
vector_store_service = None
retriever_service = None
reranker_service = None
llm_service = None
tokenizer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    global chunking_service, embedding_service, vector_store_service
    global retriever_service, reranker_service, llm_service, tokenizer
    
    # Initialize services
    chunking_service = ChunkingService(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    embedding_service = EmbeddingService(
        api_key=settings.cohere_api_key,
        model=settings.embedding_model
    )
    
    vector_store_service = VectorStoreService(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=settings.qdrant_collection_name,
        dimension=settings.embedding_dimension
    )
    
    retriever_service = RetrieverService(
        vector_store=vector_store_service,
        embedding_service=embedding_service
    )
    
    reranker_service = RerankerService(
        api_key=settings.cohere_api_key
    )
    
    llm_service = LLMService(
        api_key=settings.groq_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens
    )
    
    tokenizer = tiktoken.get_encoding("cl100k_base")
    
    yield
    
    # Cleanup (if needed)


app = FastAPI(
    title="Mini RAG API",
    description="A mini RAG system with retrieval, reranking, and LLM answering",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Mini RAG API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "ingest": "/ingest",
            "query": "/query"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        collection_info = vector_store_service.get_collection_info()
        
        return HealthResponse(
            status="healthy",
            qdrant_connected=collection_info.get("exists", False),
            collection_exists=collection_info.get("exists", False),
            document_count=collection_info.get("points_count", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest):
    """
    Ingest a document into the RAG system.
    
    Process:
    1. Chunk the text
    2. Generate embeddings
    3. Store in vector database
    """
    try:
        start_time = time.time()
        
        # Chunk the text
        chunks = chunking_service.chunk_text(
            text=request.text,
            title=request.title,
            source=request.source
        )
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks created from text")
        
        # Extract texts and metadata
        texts = [chunk["text"] for chunk in chunks]
        metadatas = chunks
        
        # Generate embeddings
        embeddings = embedding_service.batch_embed_documents(texts)
        
        # Store in vector database
        document_id = vector_store_service.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        elapsed_time = time.time() - start_time
        
        return IngestResponse(
            message=f"Document ingested successfully in {elapsed_time:.2f}s",
            chunks_created=len(chunks),
            document_id=document_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system.
    
    Process:
    1. Retrieve relevant chunks
    2. Rerank chunks
    3. Generate answer with LLM
    4. Return answer with citations
    """
    try:
        timing = {}
        
        # Step 1: Retrieval
        start_time = time.time()
        retrieved_docs = retriever_service.retrieve(
            query=request.query,
            top_k=settings.top_k,
            use_mmr=True
        )
        timing["retrieval"] = time.time() - start_time
        
        if not retrieved_docs:
            return QueryResponse(
                answer="I don't have any relevant information to answer this question.",
                sources=[],
                timing=timing,
                cost_estimate={},
                has_answer=False
            )
        
        # Step 2: Reranking
        start_time = time.time()
        reranked_docs = reranker_service.rerank(
            query=request.query,
            documents=retrieved_docs,
            top_n=settings.rerank_top_n
        )
        timing["reranking"] = time.time() - start_time
        
        # Step 3: Generate answer
        start_time = time.time()
        answer, has_answer = llm_service.generate_answer(
            query=request.query,
            contexts=reranked_docs
        )
        timing["llm"] = time.time() - start_time
        timing["total"] = sum(timing.values())
        
        # Step 4: Format sources
        sources = []
        for idx, doc in enumerate(reranked_docs, 1):
            sources.append(SourceChunk(
                text=doc["text"],
                source=doc.get("source"),
                title=doc.get("title"),
                chunk_index=doc.get("chunk_index", 0),
                score=doc.get("rerank_score", doc.get("score", 0.0))
            ))
        
        # Estimate costs
        prompt_text = f"{request.query} " + " ".join([d["text"] for d in reranked_docs])
        prompt_tokens = len(tokenizer.encode(prompt_text))
        completion_tokens = len(tokenizer.encode(answer))
        cost_estimate = llm_service.estimate_cost(prompt_tokens, completion_tokens)
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            timing={k: round(v, 3) for k, v in timing.items()},
            cost_estimate=cost_estimate,
            has_answer=has_answer
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
