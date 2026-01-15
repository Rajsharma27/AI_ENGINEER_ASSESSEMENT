import React, { useState } from 'react';
import './QueryInterface.css';

const QueryInterface = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const { queryRAG } = await import('../services/api');
    const response = await queryRAG(query);

    setLoading(false);

    if (response.success) {
      setResult(response.data);
    } else {
      setError(response.error);
    }
  };

  const formatTime = (seconds) => {
    return `${(seconds * 1000).toFixed(0)}ms`;
  };

  const formatCost = (cost) => {
    return `$${cost.toFixed(6)}`;
  };

  return (
    <div className="query-interface">
      <form onSubmit={handleSubmit}>
        <div className="query-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question about your documents..."
            disabled={loading}
            className="query-input"
          />
          <button 
            type="submit" 
            className="btn-query"
            disabled={loading || !query.trim()}
          >
            {loading ? '⏳' : '🔍'} {loading ? 'Searching...' : 'Ask'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="results">
          <div className="answer-section">
            <h3>📝 Answer</h3>
            <div className="answer-text">
              {result.answer}
            </div>
          </div>

          {result.sources && result.sources.length > 0 && (
            <div className="sources-section">
              <h3>📚 Sources ({result.sources.length})</h3>
              <div className="sources-list">
                {result.sources.map((source, idx) => (
                  <div key={idx} className="source-card">
                    <div className="source-header">
                      <span className="source-number">#{idx + 1}</span>
                      <span className="source-score">
                        Score: {source.score.toFixed(3)}
                      </span>
                    </div>
                    {(source.title || source.source) && (
                      <div className="source-meta">
                        {source.title && (
                          <div className="source-title">📄 {source.title}</div>
                        )}
                        {source.source && (
                          <div className="source-origin">🔗 {source.source}</div>
                        )}
                        <div className="source-chunk">Chunk {source.chunk_index}</div>
                      </div>
                    )}
                    <div className="source-text">{source.text}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="metadata-section">
            <div className="metadata-grid">
              <div className="metadata-card">
                <h4>⏱️ Timing</h4>
                <div className="metadata-content">
                  {Object.entries(result.timing).map(([key, value]) => (
                    <div key={key} className="metadata-row">
                      <span className="metadata-key">{key}:</span>
                      <span className="metadata-value">{formatTime(value)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="metadata-card">
                <h4>💰 Cost Estimate</h4>
                <div className="metadata-content">
                  {Object.entries(result.cost_estimate).map(([key, value]) => (
                    <div key={key} className="metadata-row">
                      <span className="metadata-key">{key}:</span>
                      <span className="metadata-value">
                        {typeof value === 'number' ? formatCost(value) : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryInterface;
