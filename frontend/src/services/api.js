/**
 * DEMAND-24 — API Service Layer
 */

import axios from 'axios';
import { supabase } from './supabaseClient';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para inyectar el token de Supabase en cada peticion
apiClient.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  return config;
});

// ── Auth ─────────────────────────────────────────────────────

export const login = async (email, password) => {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data;
};

export const register = async (email, password, fullName) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { data: { full_name: fullName } }
  });
  if (error) throw error;
  return data;
};

export const logout = async () => {
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
};

export const getCurrentUser = async () => {
  const { data: { user } } = await supabase.auth.getUser();
  return user;
};

// ── Dashboard ────────────────────────────────────────────────

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

export const acknowledgeAlert = async (alertId) => {
  const response = await apiClient.patch(`/alerts/${alertId}/acknowledge`);
  return response.data;
};

export default apiClient;
