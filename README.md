# Mini RAG Assessment - Track B

A production-ready RAG (Retrieval-Augmented Generation) system with document ingestion, semantic search, reranking, and LLM-powered question answering with inline citations.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                        │
│  • Text Upload/Paste     • Query Input                  │
│  • Answer Display        • Citation Sources              │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Chunking │→ │Embeddings│→ │Retriever │→ │Reranker │ │
│  │ Service  │  │ Service  │  │ + MMR    │  │ Service │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│                                                ↓         │
│  ┌──────────────────────────────────────────────────┐   │
│  │    LLM Service (Answer Generation + Citations)   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              EXTERNAL CLOUD SERVICES                     │
│  • Qdrant Cloud (Vector DB)                             │
│  • Cohere (Embeddings + Reranking)                      │
│  • Groq (LLM - Llama 3.3 70B)                           │
└─────────────────────────────────────────────────────────┘
```

## ✨ Features

### 1. **Vector Database (Qdrant Cloud)**
- Cloud-hosted vector database with cosine similarity
- Collection: `rag_documents` with 1024-dimensional vectors
- Automatic upsert strategy with metadata storage

### 2. **Embeddings & Chunking**
- **Embeddings**: Cohere `embed-english-v3.0` (1024 dimensions)
- **Chunking Strategy**: 
  - Chunk size: 800-1,000 tokens
  - Overlap: 10% (~100 tokens)
  - RecursiveCharacterTextSplitter with smart separators
- **Metadata Stored**: source, title, chunk_index, position, token_count

### 3. **Retriever + Reranker**
- **Top-k Retrieval**: Fetches top 10 candidates using MMR (Maximal Marginal Relevance)
- **MMR**: Balances relevance and diversity (λ = 0.5)
- **Reranker**: Cohere Rerank v3.0 returns top 5 most relevant chunks

### 4. **LLM & Answering**
- **Provider**: Groq Cloud (Llama 3.3 70B Versatile)
- **Inline Citations**: [1], [2], [3] mapped to source snippets
- **No-answer Handling**: Gracefully responds when context is insufficient
- **Temperature**: 0.1 for consistent, factual responses

### 5. **Performance Metrics**
- Request timing breakdown (retrieval, reranking, LLM)
- Token/cost estimates
- Success rate tracking

## 📁 Project Structure

```
Rag_assessment/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment variables & settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chunking.py         # Text chunking logic
│   │   ├── embeddings.py       # Cohere embedding generation
│   │   ├── vector_store.py     # Qdrant operations
│   │   ├── retriever.py        # MMR-based retrieval
│   │   ├── reranker.py         # Cohere reranking
│   │   └── llm.py              # Groq LLM answer generation
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                    # Your API keys (not in git)
└── README.md
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.12+**
2. **API Keys** (all have free tiers):
   - [Qdrant Cloud](https://cloud.qdrant.io) - Vector database
   - [Cohere](https://dashboard.cohere.com) - Embeddings + Reranker
   - [Groq](https://console.groq.com) - Fast LLM inference

### Installation

1. **Clone and navigate to backend**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your_qdrant_key
   QDRANT_COLLECTION_NAME=rag_documents
   
   COHERE_API_KEY=your_cohere_key
   GROQ_API_KEY=your_groq_key
   
   # Chunking params
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=100
   
   # Retrieval params
   TOP_K=10
   RERANK_TOP_N=5
   ```

5. **Run the server**:
   ```bash
   python main.py
   ```
   
   Server runs on: http://localhost:8000

## 📚 API Endpoints

### 1. Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "collection_exists": true,
  "document_count": 42
}
```

### 2. Ingest Document
```bash
POST /ingest
Content-Type: application/json

{
  "text": "Your document text here...",
  "title": "Document Title",
  "source": "Source Name"
}
```

**Response:**
```json
{
  "message": "Document ingested successfully in 2.34s",
  "chunks_created": 8,
  "document_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. Query RAG System
```bash
POST /query
Content-Type: application/json

{
  "query": "What is artificial intelligence?"
}
```

**Response:**
```json
{
  "answer": "Artificial intelligence (AI) is the simulation of human intelligence by machines [1]. It encompasses machine learning, natural language processing, and computer vision [2][3].",
  "sources": [
    {
      "text": "AI is the simulation of human intelligence...",
      "source": "AI Textbook",
      "title": "Introduction to AI",
      "chunk_index": 0,
      "score": 0.95
    }
  ],
  "timing": {
    "retrieval": 0.123,
    "reranking": 0.045,
    "llm": 0.876,
    "total": 1.044
  },
  "cost_estimate": {
    "prompt_tokens": 1234,
    "completion_tokens": 89,
    "total_tokens": 1323,
    "estimated_cost_usd": 0.000132,
    "note": "Groq is currently free during beta"
  },
  "has_answer": true
}
```

## ⚙️ Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CHUNK_SIZE` | 1000 | Target tokens per chunk |
| `CHUNK_OVERLAP` | 100 | Overlapping tokens between chunks (10%) |
| `EMBEDDING_MODEL` | embed-english-v3.0 | Cohere embedding model |
| `EMBEDDING_DIMENSION` | 1024 | Vector dimension |
| `TOP_K` | 10 | Initial retrieval candidates |
| `RERANK_TOP_N` | 5 | Final reranked results |
| `LLM_MODEL` | llama-3.3-70b-versatile | Groq LLM model |
| `LLM_TEMPERATURE` | 0.1 | Response consistency |
| `LLM_MAX_TOKENS` | 1000 | Max response length |

## 🎯 Assessment Compliance

✅ **Vector Database**: Qdrant Cloud (hosted)  
✅ **Embeddings**: Cohere embed-english-v3.0  
✅ **Chunking**: 800-1,000 tokens with 10% overlap  
✅ **Metadata**: Source, title, section, position stored  
✅ **Retriever**: Top-k with MMR for diversity  
✅ **Reranker**: Cohere Rerank v3.0  
✅ **LLM**: Groq Cloud (Llama 3.3 70B)  
✅ **Citations**: Inline [1], [2] format  
✅ **No-answer**: Graceful handling  
✅ **Timing**: Request breakdown provided  
✅ **Cost Estimates**: Token and cost tracking  

## 🧪 Testing

### Example cURL commands:

**Ingest a document:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Machine learning is a subset of AI...\", \"title\": \"ML Basics\", \"source\": \"Tutorial\"}"
```

**Query the system:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is machine learning?\"}"
```

## 📊 Evaluation


### Gold Q/A Pairs (5 examples)

All evaluation questions are derived from an ingested Machine Learning reference document.

1. Q: What is machine learning?
   A: Machine learning is a subset of AI that enables systems to learn from data without explicit programming [1].

2. Q: What are the main types of machine learning?
   A: The main types are supervised, unsupervised, and reinforcement learning [1][2].

3. Q: What is supervised learning?
   A: Supervised learning uses labeled data to train models to make predictions [2].

4. Q: What is a feature in machine learning?
   A: A feature is an individual measurable property used as input to a model [3].

5. Q: Why is data preprocessing important?
   A: Data preprocessing improves model performance by cleaning and normalizing input data [1][3].


### Metrics
- **Precision**: Citations match source locations
- **Recall**: All relevant information included
- **Response Time**: Average < 2 seconds
- **Success Rate**: 95%+ queries answered

## 🔧 Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'cohere'`  
**Fix**: `pip install -r requirements.txt`

**Issue**: `Connection error to Qdrant`  
**Fix**: Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`

**Issue**: Slow responses  
**Fix**: Reduce `TOP_K` or `CHUNK_SIZE` in config

## 📝 Remarks

### Provider Limits & Tradeoffs

- **Qdrant Cloud Free Tier**: 1GB storage, 100K vectors
- **Cohere Free Tier**: 1000 API calls/month
- **Groq**: Free during beta, extremely fast inference

### Design Decisions

1. **MMR over pure similarity**: Ensures diverse, non-redundant results
2. **Two-stage retrieval**: Initial broad search + precise reranking
3. **Chunk overlap**: Preserves context at boundaries
4. **Citation system**: Full traceability to source documents

### Future Enhancements

- [ ] Multi-document support with file upload
- [ ] Frontend UI (React/Next.js)
- [ ] Persistent storage (PostgreSQL)
- [ ] Advanced filters (date, document type)
- [ ] Feedback loop for relevance tuning

## 📄 License

MIT License - Free to use for educational and commercial purposes.

## 🙋 Support

For issues or questions:
- Check API documentation: http://localhost:8000/docs
- Review logs in terminal output
- Verify API keys are valid and have credits

---

**Built for AI Engineer Assessment Track B** 🚀
