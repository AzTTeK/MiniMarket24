/**
 * DEMAND-24 — API Service Layer
 *
 * Cliente HTTP centralizado para comunicacion con el backend FastAPI.
 * Todos los endpoints se consumen a traves de este modulo.
 *
 * Cumple con:
 * - Regla I: Frontend es "tonto" — solo consume datos via REST
 * - Regla II: Wrapper sobre Axios para agnosticismo de dependencia
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Dashboard ────────────────────────────────────────────────

/**
 * Obtiene el resumen completo del dashboard.
 * Incluye KPIs, lista de productos y datos de graficos.
 */
export const getDashboardSummary = async () => {
  const response = await apiClient.get('/dashboard/summary');
  return response.data;
};

// ── SKUs ─────────────────────────────────────────────────────

export const getSkus = async () => {
  const response = await apiClient.get('/skus');
  return response.data;
};

// ── Predictions ──────────────────────────────────────────────

export const getPredictions = async () => {
  const response = await apiClient.get('/predictions');
  return response.data;
};

export const getPredictionsBySku = async (skuId) => {
  const response = await apiClient.get(`/predictions/${skuId}`);
  return response.data;
};

// ── Training ─────────────────────────────────────────────────

export const triggerTraining = async () => {
  const response = await apiClient.post('/training');
  return response.data;
};

// ── Alerts ───────────────────────────────────────────────────

export const getAlerts = async () => {
  const response = await apiClient.get('/alerts');
  return response.data;
};

export const getAllAlerts = async () => {
  const response = await apiClient.get('/alerts/all');
  return response.data;
};

export const acknowledgeAlert = async (alertId) => {
  const response = await apiClient.patch(`/alerts/${alertId}/acknowledge`);
  return response.data;
};

// ── Health ───────────────────────────────────────────────────

export const getHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export default apiClient;
