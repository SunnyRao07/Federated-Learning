/**
 * API client for federated learning backend
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Training endpoints
export const trainModel = (config) => api.post('/train', config);
export const getMetrics = () => api.get('/metrics');
export const getStatus = () => api.get('/status');
export const getHistory = () => api.get('/history');
export const getClients = () => api.get('/clients');
export const resetTraining = () => api.delete('/reset');

// Prediction endpoints
export const predictFraud = (features) => api.post('/predict', { features });

// Privacy attack endpoints
export const runAttackTest = () => api.get('/attack-test');

export default api;
