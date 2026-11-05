export interface HealthResponse {
  status: string;
  service: string;
}

export interface ReadyResponse {
  status: string;
  service: string;
  database: string;
}

export type ConnectionState = 'checking' | 'connected' | 'unavailable';

export interface DiagnosticsState {
  frontend: ConnectionState;
  backend: ConnectionState;
  database: ConnectionState;
  lastChecked: string | null;
  backendMessage?: string;
  databaseMessage?: string;
  errorDetail?: string;
}

