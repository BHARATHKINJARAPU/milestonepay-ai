import React, { useEffect, useState } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  RefreshCw, 
  Server, 
  Database, 
  Globe, 
  AlertTriangle,
  ExternalLink
} from 'lucide-react';
import { checkApiHealth, checkDatabaseReadiness, API_BASE_URL } from '../../lib/api';
import { DiagnosticsState, ConnectionState } from '../../types/health';

export const ConnectionStatus: React.FC = () => {
  const [status, setStatus] = useState<DiagnosticsState>({
    frontend: 'connected',
    backend: 'checking',
    database: 'checking',
    lastChecked: null,
    backendMessage: undefined,
    databaseMessage: undefined,
    errorDetail: undefined,
  });

  const [isLoading, setIsLoading] = useState(false);

  const runDiagnostics = async () => {
    setIsLoading(true);
    const now = new Date().toLocaleTimeString();

    setStatus(prev => ({
      ...prev,
      frontend: 'connected',
      backend: 'checking',
      database: 'checking',
      errorDetail: undefined,
    }));

    let backendResult: ConnectionState = 'unavailable';
    let databaseResult: ConnectionState = 'unavailable';
    let backendMsg = '';
    let dbMsg = '';
    let errDetail: string | undefined = undefined;

    // 1. Verify Backend API Health
    try {
      const healthData = await checkApiHealth();
      if (healthData.status === 'ok') {
        backendResult = 'connected';
        backendMsg = `${healthData.service} (${healthData.status})`;
      } else {
        backendMsg = 'Unexpected health response';
      }
    } catch (err: unknown) {
      backendResult = 'unavailable';
      backendMsg = err instanceof Error ? err.message : 'Backend unreachable';
      errDetail = `Backend Error: ${backendMsg}`;
    }

    // 2. Verify PostgreSQL Readiness via Backend
    try {
      const readyData = await checkDatabaseReadiness();
      if (readyData.status === 'ready' && readyData.database === 'connected') {
        databaseResult = 'connected';
        dbMsg = `PostgreSQL: ${readyData.database}`;
      } else {
        databaseResult = 'unavailable';
        dbMsg = `Unexpected database status: ${readyData.database}`;
      }
    } catch (err: unknown) {
      databaseResult = 'unavailable';
      dbMsg = err instanceof Error ? err.message : 'Database check failed';
      if (!errDetail) {
        errDetail = `Database Error: ${dbMsg}`;
      }
    }

    setStatus({
      frontend: 'connected',
      backend: backendResult,
      database: databaseResult,
      lastChecked: now,
      backendMessage: backendMsg,
      databaseMessage: dbMsg,
      errorDetail: errDetail,
    });

    setIsLoading(false);
  };

  useEffect(() => {
    runDiagnostics();
  }, []);

  const getStatusBadge = (state: ConnectionState) => {
    switch (state) {
      case 'connected':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Connected
          </span>
        );
      case 'checking':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            Checking...
          </span>
        );
      case 'unavailable':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <XCircle className="w-3.5 h-3.5" />
            Unavailable
          </span>
        );
    }
  };

  const allConnected =
    status.frontend === 'connected' &&
    status.backend === 'connected' &&
    status.database === 'connected';

  return (
    <section id="system-status" className="py-16 bg-slate-950/80 border-t border-slate-900 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 backdrop-blur-xl shadow-2xl">
          {/* Card Header */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${allConnected ? 'bg-emerald-400' : 'bg-amber-400'} animate-pulse`} />
                <h3 className="text-xl font-bold text-white tracking-tight">
                  Day 1 Technical Foundation Diagnostics
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Real-time health verification across Frontend, FastAPI, and PostgreSQL layers.
              </p>
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-end">
              {status.lastChecked && (
                <span className="text-[11px] text-slate-400 font-mono">
                  Checked: {status.lastChecked}
                </span>
              )}
              <button
                type="button"
                onClick={runDiagnostics}
                disabled={isLoading}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700/80 text-white text-xs font-semibold border border-slate-700 transition-all flex items-center gap-2 disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                <span>{isLoading ? 'Verifying...' : 'Retry Connection'}</span>
              </button>
            </div>
          </div>

          {/* 3 Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6">
            {/* Frontend Card */}
            <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 text-slate-200">
                  <Globe className="w-4 h-4 text-blue-400" />
                  <span className="text-sm font-semibold">React + Vite Client</span>
                </div>
                {getStatusBadge(status.frontend)}
              </div>
              <div className="space-y-1 text-[11px] font-mono text-slate-400">
                <div className="flex justify-between">
                  <span>Host:</span>
                  <span className="text-slate-300">http://localhost:5173</span>
                </div>
                <div className="flex justify-between">
                  <span>Renderer:</span>
                  <span className="text-slate-300">Active (DOM OK)</span>
                </div>
              </div>
            </div>

            {/* Backend API Card */}
            <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 text-slate-200">
                  <Server className="w-4 h-4 text-indigo-400" />
                  <span className="text-sm font-semibold">FastAPI Backend</span>
                </div>
                {getStatusBadge(status.backend)}
              </div>
              <div className="space-y-1 text-[11px] font-mono text-slate-400">
                <div className="flex justify-between">
                  <span>Endpoint:</span>
                  <span className="text-slate-300">GET /api/v1/health</span>
                </div>
                <div className="flex justify-between truncate">
                  <span>Status:</span>
                  <span className="text-slate-300 truncate max-w-[150px]">{status.backendMessage || 'Awaiting response'}</span>
                </div>
              </div>
            </div>

            {/* Database Card */}
            <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 text-slate-200">
                  <Database className="w-4 h-4 text-violet-400" />
                  <span className="text-sm font-semibold">PostgreSQL Database</span>
                </div>
                {getStatusBadge(status.database)}
              </div>
              <div className="space-y-1 text-[11px] font-mono text-slate-400">
                <div className="flex justify-between">
                  <span>Readiness:</span>
                  <span className="text-slate-300">GET /api/v1/health/ready</span>
                </div>
                <div className="flex justify-between truncate">
                  <span>Query Test:</span>
                  <span className="text-slate-300 truncate max-w-[150px]">{status.databaseMessage || 'SELECT 1'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Error / Assistance Banner */}
          {status.errorDetail && (
            <div className="mt-6 p-4 rounded-xl bg-rose-950/40 border border-rose-900/60 flex items-start gap-3 text-xs text-rose-300">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="font-semibold text-rose-200">Connection Attention Required</p>
                <p className="font-mono">{status.errorDetail}</p>
                <p className="text-slate-400 text-[11px]">
                  Ensure FastAPI is running (<code className="text-rose-300 bg-rose-950/60 px-1 py-0.5 rounded">uvicorn app.main:app --reload</code>) and PostgreSQL is accessible at <code className="text-rose-300 bg-rose-950/60 px-1 py-0.5 rounded">localhost:5432</code>.
                </p>
              </div>
            </div>
          )}

          {/* Quick links to swagger and backend */}
          <div className="mt-6 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-400">
            <div className="flex items-center gap-4">
              <a
                href={`${API_BASE_URL}/docs`}
                target="_blank"
                rel="noreferrer"
                className="hover:text-blue-400 transition-colors flex items-center gap-1"
              >
                <span>Interactive Swagger UI</span>
                <ExternalLink className="w-3 h-3" />
              </a>
              <span>•</span>
              <a
                href={`${API_BASE_URL}/api/v1/health`}
                target="_blank"
                rel="noreferrer"
                className="hover:text-blue-400 transition-colors flex items-center gap-1"
              >
                <span>/api/v1/health</span>
                <ExternalLink className="w-3 h-3" />
              </a>
              <span>•</span>
              <a
                href={`${API_BASE_URL}/api/v1/health/ready`}
                target="_blank"
                rel="noreferrer"
                className="hover:text-blue-400 transition-colors flex items-center gap-1"
              >
                <span>/api/v1/health/ready</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            <div className="font-mono text-[11px] text-slate-400">
              Base URL: {API_BASE_URL}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

