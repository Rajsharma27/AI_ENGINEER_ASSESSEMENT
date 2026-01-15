import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const ingestDocument = async (text, title, source) => {
  try {
    const response = await api.post('/ingest', {
      text,
      title: title || null,
      source: source || null,
    });
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || error.message 
    };
  }
};

export const queryRAG = async (query) => {
  try {
    const response = await api.post('/query', { query });
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || error.message 
    };
  }
};

export default api;
