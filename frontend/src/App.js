import React, { useState, useEffect } from 'react';
import './App.css';
import DocumentIngestion from './components/DocumentIngestion';
import QueryInterface from './components/QueryInterface';
import { healthCheck } from './services/api';

function App() {
  const [healthStatus, setHealthStatus] = useState({
    status: 'checking',
    qdrant_connected: false,
    collection_exists: false,
    document_count: 0
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    const result = await healthCheck();
    if (result.success) {
      setHealthStatus(result.data);
    } else {
      setHealthStatus({
        status: 'error',
        qdrant_connected: false,
        collection_exists: false,
        document_count: 0
      });
    }
  };

  const handleIngestComplete = () => {
    // Refresh health status to update document count
    checkHealth();
  };

  return (
    <div className="App">
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Processing...</p>
          </div>
        </div>
      )}

      <div className="container">
        <header className="header">
          <h1>🤖 Mini RAG Assessment</h1>
          <p>Document Ingestion & Intelligent Question Answering System</p>
        </header>

        <div className="main-content">
          <div className="card">
            <h2>📤 Ingest Document</h2>
            <DocumentIngestion onIngestComplete={handleIngestComplete} />
          </div>

          <div className="card">
            <h2>💬 Ask Questions</h2>
            <QueryInterface />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
