import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { HealthResponse, ReadyResponse } from '../types/health';
import { LoginRequest, RegisterRequest, TokenResponse, User } from '../types/auth';
import { Project, ProjectCreateInput, ProjectListResponse, ProjectStatus, ProjectUpdateInput } from '../types/project';

// Read API Base URL from Vite environment with localhost fallback
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');

/**
 * Storage Note:
 * For this Day 2 MVP, access tokens are persisted in session-scoped storage (sessionStorage)
 * to balance simplicity with protection against multi-tab leakage upon browser closure.
 * Production deployments should consider secure HttpOnly cookies with CSRF defense.
 */
export const AUTH_TOKEN_KEY = 'mp_auth_token';

// Create configured Axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Interceptor to attach Bearer token automatically if available
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = sessionStorage.getItem(AUTH_TOKEN_KEY);
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function handleAxiosError(error: unknown, fallbackMessage: string): never {
  const err = error as AxiosError<{ detail?: string | Array<{ msg: string }> }>;
  let message = fallbackMessage;

  if (err.response?.data?.detail) {
    const detail = err.response.data.detail;
    if (typeof detail === 'string') {
      message = detail;
    } else if (Array.isArray(detail) && detail.length > 0) {
      message = detail.map(d => d.msg).join(', ');
    }
  } else if (err.message) {
    message = err.message;
  }
  throw new Error(message);
}

/* ==========================================================================
   DAY 1: HEALTH & DIAGNOSTICS
   ========================================================================== */

export async function checkApiHealth(): Promise<HealthResponse> {
  try {
    const response = await apiClient.get<HealthResponse>('/api/v1/health');
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'API connection failed');
  }
}

export async function checkDatabaseReadiness(): Promise<ReadyResponse> {
  try {
    const response = await apiClient.get<ReadyResponse>('/api/v1/health/ready');
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Database readiness verification failed');
  }
}

/* ==========================================================================
   DAY 2: AUTHENTICATION API
   ========================================================================== */

export async function registerUser(payload: RegisterRequest): Promise<User> {
  try {
    const response = await apiClient.post<User>('/api/v1/auth/register', payload);
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Registration failed. Please check form details.');
  }
}

export async function loginUser(payload: LoginRequest): Promise<TokenResponse> {
  try {
    const response = await apiClient.post<TokenResponse>('/api/v1/auth/login', payload);
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Login failed. Please verify your credentials.');
  }
}

export async function getCurrentUser(): Promise<User> {
  try {
    const response = await apiClient.get<User>('/api/v1/auth/me');
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to fetch current user session.');
  }
}

/* ==========================================================================
   DAY 2: PROJECT MANAGEMENT API
   ========================================================================== */

export async function getProjects(status?: ProjectStatus): Promise<Project[]> {
  try {
    const params = status ? { status } : {};
    const response = await apiClient.get<ProjectListResponse>('/api/v1/projects', { params });
    return response.data.projects;
  } catch (error) {
    handleAxiosError(error, 'Failed to fetch projects.');
  }
}

export async function getProject(id: string): Promise<Project> {
  try {
    const response = await apiClient.get<Project>(`/api/v1/projects/${id}`);
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve project details.');
  }
}

export async function createProject(payload: ProjectCreateInput): Promise<Project> {
  try {
    const response = await apiClient.post<Project>('/api/v1/projects', payload);
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to create project.');
  }
}

export async function updateProject(id: string, payload: ProjectUpdateInput): Promise<Project> {
  try {
    const response = await apiClient.patch<Project>(`/api/v1/projects/${id}`, payload);
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to update project details.');
  }
}

export async function addProjectMember(id: string, email: string): Promise<Project> {
  try {
    const response = await apiClient.post<Project>(`/api/v1/projects/${id}/members`, { email });
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to add collaborator.');
  }
}

export async function updateProjectStatus(id: string, status: ProjectStatus): Promise<Project> {
  try {
    const response = await apiClient.patch<Project>(`/api/v1/projects/${id}/status`, { status });
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to update project status.');
  }
}

export { API_BASE_URL };
