import axios, { AxiosError } from 'axios';
import { HealthResponse, ReadyResponse } from '../types/health';

// Read API Base URL from Vite environment with localhost fallback
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');

// Create configured Axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

/**
 * Checks basic backend API connectivity.
 * Calls: GET /api/v1/health
 */
export async function checkApiHealth(): Promise<HealthResponse> {
  try {
    const response = await apiClient.get<HealthResponse>('/api/v1/health');
    return response.data;
  } catch (error) {
    const err = error as AxiosError<{ detail?: string }>;
    const message = err.response?.data?.detail || err.message || 'API connection failed';
    throw new Error(message);
  }
}

/**
 * Checks API and PostgreSQL database readiness.
 * Calls: GET /api/v1/health/ready (executes SELECT 1 on backend)
 */
export async function checkDatabaseReadiness(): Promise<ReadyResponse> {
  try {
    const response = await apiClient.get<ReadyResponse>('/api/v1/health/ready');
    return response.data;
  } catch (error) {
    const err = error as AxiosError<{ detail?: string }>;
    const message = err.response?.data?.detail || err.message || 'Database readiness verification failed';
    throw new Error(message);
  }
}

export { API_BASE_URL };
