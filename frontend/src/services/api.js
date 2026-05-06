import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // SKUs
  getSkus: () => apiClient.get('/skus'),
  getSkuById: (id) => apiClient.get(`/skus/${id}`),

  // Predictions
  getPredictions: (skuId) => apiClient.get(`/predictions/${skuId}`),
  
  // Alerts
  getAlerts: () => apiClient.get('/alerts'),
  checkStock: (stockLevels) => apiClient.post('/alerts/check-stock', { stock_levels: stockLevels }),
  acknowledgeAlert: (id) => apiClient.patch(`/alerts/${id}/acknowledge`),

  // Training
  triggerTraining: () => apiClient.post('/training'),
  
  // Health
  getHealth: () => apiClient.get('/health'),
};

export default apiService;
