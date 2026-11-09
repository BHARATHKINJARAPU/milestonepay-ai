import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { HealthResponse, ReadyResponse } from '../types/health';
import { LoginRequest, RegisterRequest, TokenResponse, User } from '../types/auth';
import { Project, ProjectCreateInput, ProjectListResponse, ProjectStatus, ProjectUpdateInput } from '../types/project';
import {
  CreateManualPlanInput,
  GenerateMilestonePlanInput,
  MilestonePlan,
  MilestonePlanListResponse,
  UpdateMilestonePlanInput,
} from '../types/milestone';
import {
  CreateSubmissionInput,
  MilestoneSubmission,
  MilestoneSubmissionListResponse,
} from '../types/submission';
import {
  Notification,
  NotificationListResponse,
  UnreadCountResponse,
} from '../types/notification';
import {
  ProjectActivityListResponse,
} from '../types/activity';
import {
  DashboardAnalytics,
  PaymentAnalytics,
  ProjectAiSummary,
} from '../types/analytics';

// Read API Base URL from Vite environment.
// In development, an empty string allows same-origin relative requests via the Vite reverse proxy (e.g., /api/v1/auth/register).
// In production, VITE_API_BASE_URL specifies the deployed backend API URL (e.g., https://api.milestonepay.ai).
const rawBaseUrl = import.meta.env.VITE_API_BASE_URL;
const API_BASE_URL = (rawBaseUrl && typeof rawBaseUrl === 'string' && rawBaseUrl.trim() !== '')
  ? rawBaseUrl.trim().replace(/\/+$/, '')
  : '';

/**
 * Storage Note:
 * Access tokens are persisted in session-scoped storage (sessionStorage)
 * to balance simplicity with protection against multi-tab leakage upon browser closure.
 * Production deployments can utilize secure HttpOnly cookies with CSRF defense.
 */
export const AUTH_TOKEN_KEY = 'mp_auth_token';

// Create configured Axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
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

  // Safe developer diagnostics (never log passwords, tokens, or credentials)
  if (import.meta.env.DEV) {
    const method = err.config?.method?.toUpperCase() || 'UNKNOWN';
    const url = err.config?.url || 'UNKNOWN';
    const status = err.response?.status;
    console.warn(`[MilestonePay API Error] ${method} ${url} -> Status: ${status ?? 'NO_RESPONSE'} (${err.code || 'ERR_UNKNOWN'})`);
  }

  if (err.response?.data?.detail) {
    const detail = err.response.data.detail;
    if (typeof detail === 'string') {
      message = detail;
    } else if (Array.isArray(detail) && detail.length > 0) {
      message = detail.map(d => d.msg).join(', ');
    }
  } else if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
    message = 'Unable to connect to the backend server. Please verify the backend is running and the proxy/network connection is reachable.';
  } else if (err.code === 'ECONNABORTED' || err.message?.toLowerCase().includes('timeout')) {
    message = 'Request timed out waiting for the server to respond. Please try again.';
  } else if (err.response?.status === 404) {
    message = 'The requested service endpoint was not found (404).';
  } else if (err.response?.status === 500) {
    message = 'Internal server error occurred. Please try again shortly or contact support.';
  } else if (err.response?.status === 502 || err.response?.status === 503) {
    message = 'Backend service is currently unavailable. Please verify the backend server is active.';
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

/* ==========================================================================
   DAY 3: GEMINI AI MILESTONE & AGREEMENT API
   ========================================================================== */

export async function generateMilestonePlan(
  projectId: string,
  payload: GenerateMilestonePlanInput = {}
): Promise<MilestonePlan> {
  try {
    // Extended timeout for Gemini AI generative reasoning
    const response = await apiClient.post<MilestonePlan>(
      `/api/v1/projects/${projectId}/milestone-plans/generate`,
      payload,
      { timeout: 60000 }
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to generate milestone plan with Gemini AI.');
  }
}

export async function createManualMilestonePlan(
  projectId: string,
  payload: CreateManualPlanInput
): Promise<MilestonePlan> {
  try {
    const response = await apiClient.post<MilestonePlan>(
      `/api/v1/projects/${projectId}/milestone-plans/manual`,
      payload
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to create manual milestone plan.');
  }
}

export async function getMilestonePlans(projectId: string): Promise<MilestonePlanListResponse> {
  try {
    const response = await apiClient.get<MilestonePlanListResponse>(
      `/api/v1/projects/${projectId}/milestone-plans`
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to fetch milestone plans for this project.');
  }
}

export async function getMilestonePlan(projectId: string, planId: string): Promise<MilestonePlan> {
  try {
    const response = await apiClient.get<MilestonePlan>(
      `/api/v1/projects/${projectId}/milestone-plans/${planId}`
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve milestone plan details.');
  }
}

export async function updateMilestonePlan(
  projectId: string,
  planId: string,
  payload: UpdateMilestonePlanInput
): Promise<MilestonePlan> {
  try {
    const response = await apiClient.patch<MilestonePlan>(
      `/api/v1/projects/${projectId}/milestone-plans/${planId}`,
      payload
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to update milestone plan.');
  }
}

export async function submitMilestonePlanForApproval(
  projectId: string,
  planId: string
): Promise<MilestonePlan> {
  try {
    const response = await apiClient.post<MilestonePlan>(
      `/api/v1/projects/${projectId}/milestone-plans/${planId}/submit-for-approval`
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to submit plan for bilateral approval.');
  }
}

export async function approveMilestonePlan(
  projectId: string,
  planId: string
): Promise<MilestonePlan> {
  try {
    const response = await apiClient.post<MilestonePlan>(
      `/api/v1/projects/${projectId}/milestone-plans/${planId}/approve`
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to approve milestone plan.');
  }
}

export async function requestMilestonePlanRevision(
  projectId: string,
  planId: string,
  comment: string
): Promise<MilestonePlan> {
  try {
    const response = await apiClient.post<MilestonePlan>(
      `/api/v1/projects/${projectId}/milestone-plans/${planId}/request-revision`,
      { comment }
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to submit revision request.');
  }
}

/* ==========================================================================
   DAY 4: DELIVERABLE SUBMISSION & AI EVALUATION API
   ========================================================================== */

export async function createSubmission(
  projectId: string,
  milestoneId: string,
  payload: CreateSubmissionInput
): Promise<MilestoneSubmission> {
  try {
    const response = await apiClient.post<MilestoneSubmission>(
      `/api/v1/projects/${projectId}/milestones/${milestoneId}/submissions`,
      payload
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to create milestone submission draft.');
  }
}

export async function getMilestoneSubmissions(
  projectId: string,
  milestoneId: string
): Promise<MilestoneSubmissionListResponse> {
  try {
    const response = await apiClient.get<MilestoneSubmissionListResponse>(
      `/api/v1/projects/${projectId}/milestones/${milestoneId}/submissions`
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve milestone submissions.');
  }
}

export async function getSubmission(submissionId: string): Promise<MilestoneSubmission> {
  try {
    const response = await apiClient.get<MilestoneSubmission>(
      `/api/v1/submissions/${submissionId}`
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve submission details.');
  }
}

export async function uploadSubmissionEvidence(
  submissionId: string,
  files: File[]
): Promise<MilestoneSubmission> {
  try {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await apiClient.post<MilestoneSubmission>(
      `/api/v1/submissions/${submissionId}/evidence`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to upload evidence artifacts.');
  }
}

export async function deleteSubmissionEvidence(
  submissionId: string,
  evidenceId: string
): Promise<MilestoneSubmission> {
  try {
    const response = await apiClient.delete<MilestoneSubmission>(
      `/api/v1/submissions/${submissionId}/evidence/${evidenceId}`
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to delete evidence artifact.');
  }
}

export async function submitDeliverable(submissionId: string): Promise<MilestoneSubmission> {
  try {
    // 60-second timeout for multimodal Gemini AI evaluation reasoning
    const response = await apiClient.post<MilestoneSubmission>(
      `/api/v1/submissions/${submissionId}/submit`,
      {},
      { timeout: 60000 }
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to finalize deliverable submission.');
  }
}

export async function retryDeliverableEvaluation(
  submissionId: string
): Promise<MilestoneSubmission> {
  try {
    const response = await apiClient.post<MilestoneSubmission>(
      `/api/v1/submissions/${submissionId}/evaluate`,
      {},
      { timeout: 60000 }
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to re-run AI deliverable evaluation.');
  }
}

export async function clientApproveSubmission(
  submissionId: string,
  comment?: string
): Promise<MilestoneSubmission> {
  try {
    const response = await apiClient.post<MilestoneSubmission>(
      `/api/v1/submissions/${submissionId}/approve`,
      { decision: 'approved', comment }
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to approve milestone submission.');
  }
}

export async function clientRequestSubmissionRevision(
  submissionId: string,
  comment: string
): Promise<MilestoneSubmission> {
  try {
    const response = await apiClient.post<MilestoneSubmission>(
      `/api/v1/submissions/${submissionId}/request-revision`,
      { decision: 'revision_requested', comment }
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to request milestone revision.');
  }
}

export async function downloadEvidenceBlob(
  submissionId: string,
  evidenceId: string
): Promise<{ data: Blob; filename: string }> {
  try {
    const response = await apiClient.get<Blob>(
      `/api/v1/submissions/${submissionId}/evidence/${evidenceId}`,
      { responseType: 'blob' }
    );
    // Parse filename from Content-Disposition if present
    const disposition = response.headers['content-disposition'] || '';
    let filename = 'downloaded_evidence';
    const match = disposition.match(/filename="?([^";]+)"?/);
    if (match && match[1]) {
      filename = match[1];
    }
    return { data: response.data, filename };
  } catch (error) {
    handleAxiosError(error, 'Failed to download evidence file.');
  }
}

import {
  CreatePaymentPayload,
  MockConfirmPayload,
  Payment,
  PaymentEligibility,
  PaymentListResponse,
  PaymentStatusCheck,
} from '../types/payment';

/* ==========================================================================
   DAY 5: PAYMENT MANAGEMENT & PAYPAL SANDBOX API
   ========================================================================== */

export async function checkPaymentEligibility(
  projectId: string,
  milestoneId: string
): Promise<PaymentEligibility> {
  try {
    const response = await apiClient.get<PaymentEligibility>(
      `/api/v1/projects/${projectId}/milestones/${milestoneId}/payment-eligibility`
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to check milestone payment eligibility.');
  }
}

export async function createMilestonePayment(
  projectId: string,
  milestoneId: string,
  payload?: CreatePaymentPayload
): Promise<Payment> {
  try {
    const response = await apiClient.post<Payment>(
      `/api/v1/projects/${projectId}/milestones/${milestoneId}/payments`,
      payload || {}
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to initiate milestone payment checkout.');
  }
}

export async function capturePayment(paymentId: string): Promise<Payment> {
  try {
    const response = await apiClient.post<Payment>(
      `/api/v1/payments/${paymentId}/capture`
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to capture payment order.');
  }
}

export async function mockConfirmPayment(
  paymentId: string,
  payload: MockConfirmPayload
): Promise<Payment> {
  try {
    const response = await apiClient.post<Payment>(
      `/api/v1/payments/${paymentId}/mock-confirm`,
      payload
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to process simulated payment confirmation.');
  }
}

export async function getPayment(paymentId: string): Promise<Payment> {
  try {
    const response = await apiClient.get<Payment>(`/api/v1/payments/${paymentId}`);
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve payment details.');
  }
}

export async function getPaymentStatus(paymentId: string): Promise<PaymentStatusCheck> {
  try {
    const response = await apiClient.get<PaymentStatusCheck>(`/api/v1/payments/${paymentId}/status`);
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve payment reconciliation status.');
  }
}

export async function getPayments(params?: {
  project_id?: string;
  milestone_id?: string;
  status?: string;
  provider?: string;
}): Promise<PaymentListResponse> {
  try {
    const response = await apiClient.get<PaymentListResponse>('/api/v1/payments', {
      params,
    });
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve payment history.');
  }
}

/* ==========================================================================
   DAY 6: NOTIFICATIONS, ACTIVITIES & FINANCIAL ANALYTICS
   ========================================================================== */

export async function getNotifications(params?: {
  unread_only?: boolean;
  skip?: number;
  limit?: number;
}): Promise<NotificationListResponse> {
  try {
    const response = await apiClient.get<NotificationListResponse>('/api/v1/notifications', {
      params,
    });
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve notifications.');
  }
}

export async function getUnreadNotificationCount(): Promise<UnreadCountResponse> {
  try {
    const response = await apiClient.get<UnreadCountResponse>('/api/v1/notifications/unread-count');
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve unread notification count.');
  }
}

export async function markNotificationRead(notificationId: string): Promise<Notification> {
  try {
    const response = await apiClient.patch<Notification>(`/api/v1/notifications/${notificationId}/read`);
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to mark notification as read.');
  }
}

export async function markAllNotificationsRead(): Promise<UnreadCountResponse> {
  try {
    const response = await apiClient.patch<UnreadCountResponse>('/api/v1/notifications/read-all');
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to mark all notifications as read.');
  }
}

export async function deleteNotification(notificationId: string): Promise<void> {
  try {
    await apiClient.delete(`/api/v1/notifications/${notificationId}`);
  } catch (error) {
    handleAxiosError(error, 'Failed to delete notification.');
  }
}

export async function getProjectActivities(
  projectId: string,
  params?: { skip?: number; limit?: number }
): Promise<ProjectActivityListResponse> {
  try {
    const response = await apiClient.get<ProjectActivityListResponse>(
      `/api/v1/projects/${projectId}/activities`,
      { params }
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve project activity timeline.');
  }
}

export async function getDashboardAnalytics(): Promise<DashboardAnalytics> {
  try {
    const response = await apiClient.get<DashboardAnalytics>('/api/v1/analytics/dashboard');
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve dashboard analytics.');
  }
}

export async function getPaymentAnalytics(): Promise<PaymentAnalytics> {
  try {
    const response = await apiClient.get<PaymentAnalytics>('/api/v1/analytics/payments');
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to retrieve payment analytics.');
  }
}

export async function getProjectAiSummary(projectId: string): Promise<ProjectAiSummary> {
  try {
    const response = await apiClient.get<ProjectAiSummary>(
      `/api/v1/projects/${projectId}/ai-summary`
    );
    return response.data;
  } catch (error) {
    handleAxiosError(error, 'Failed to generate project AI summary.');
  }
}

export { API_BASE_URL };
