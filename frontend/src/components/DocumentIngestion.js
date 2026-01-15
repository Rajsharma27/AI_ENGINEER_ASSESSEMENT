import React, { useState } from 'react';
import './DocumentIngestion.css';

const DocumentIngestion = ({ onIngestComplete }) => {
  const [text, setText] = useState('');
  const [title, setTitle] = useState('');
  const [source, setSource] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setMessage({ type: 'error', text: 'Please enter some text to ingest' });
      return;
    }

    setLoading(true);
    setMessage(null);

    const { ingestDocument } = await import('../services/api');
    const result = await ingestDocument(text, title, source);

    setLoading(false);

    if (result.success) {
      setMessage({ 
        type: 'success', 
        text: `✓ ${result.data.message}\n${result.data.chunks_created} chunks created` 
      });
      setText('');
      setTitle('');
      setSource('');
      if (onIngestComplete) onIngestComplete(result.data);
    } else {
      setMessage({ type: 'error', text: `✗ ${result.error}` });
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setText(event.target.result);
        if (!title) setTitle(file.name);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="document-ingestion">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Document Title (Optional)</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Introduction to AI"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="source">Source (Optional)</label>
          <input
            type="text"
            id="source"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="e.g., AI Textbook Chapter 1"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="text">Document Text *</label>
          <textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your document text here or upload a file..."
            rows="12"
            disabled={loading}
            required
          />
        </div>

        <div className="file-upload">
          <label htmlFor="file-input" className="file-upload-label">
            📁 Upload Text File
          </label>
          <input
            id="file-input"
            type="file"
            accept=".txt,.md"
            onChange={handleFileUpload}
            disabled={loading}
          />
        </div>

        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <button 
          type="submit" 
          className="btn-primary"
          disabled={loading || !text.trim()}
        >
          {loading ? 'Processing...' : '🚀 Ingest Document'}
        </button>
      </form>
    </div>
  );
};

export default DocumentIngestion;
