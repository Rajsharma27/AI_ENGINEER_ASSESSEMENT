# RAG Assessment Frontend

React frontend for the Mini RAG (Retrieval-Augmented Generation) system.

## Features

- **Document Ingestion**: Upload and process documents with metadata
- **Intelligent Q&A**: Ask questions and get AI-powered answers with source citations
- **Real-time Status**: Monitor backend and vector database connectivity
- **Source Attribution**: View relevant document chunks with confidence scores
- **Performance Metrics**: See timing and cost estimates for each query

## Setup Instructions

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

4. Update the `.env` file if your backend runs on a different port:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

### Running the Application

1. Start the development server:
   ```bash
   npm start
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

### Building for Production

To create a production build:

```bash
npm run build
```

The optimized files will be in the `build/` directory.

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/
│   │   ├── DocumentIngestion.js    # Document upload component
│   │   ├── DocumentIngestion.css
│   │   ├── QueryInterface.js        # Q&A interface component
│   │   └── QueryInterface.css
│   ├── services/
│   │   └── api.js          # API service layer
│   ├── App.js              # Main application component
│   ├── App.css             # Main application styles
│   ├── index.js            # Application entry point
│   └── index.css           # Global styles
├── .env.example            # Environment variables template
├── .gitignore
└── package.json
```

## Usage

### Ingesting Documents

1. Enter a document title (optional)
2. Add a source reference (optional)
3. Paste text or upload a `.txt` file
4. Click "🚀 Ingest Document"

### Asking Questions

1. Type your question in the query input
2. Click "🔍 Ask"
3. View the AI-generated answer with source citations
4. Check timing and cost metrics

## API Integration

The frontend communicates with the backend through these endpoints:

- `GET /health` - Health check and status
- `POST /ingest` - Document ingestion
- `POST /query` - Question answering

## Technologies Used

- **React 18** - UI framework
- **Axios** - HTTP client
- **CSS3** - Styling
- **React Scripts** - Build tooling

## Troubleshooting

### Backend Connection Issues

If you see "Backend: Disconnected":
- Ensure the backend is running on `http://localhost:8000`
- Check CORS settings in the backend
- Verify the `REACT_APP_API_URL` in `.env`

### CORS Errors

The backend should have CORS middleware enabled. Check backend `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Contributing

Feel free to submit issues or pull requests to improve the frontend.

## License

MIT
