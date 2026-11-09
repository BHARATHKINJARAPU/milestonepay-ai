import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Lightbulb,
  Loader2,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { ProjectAiSummary } from '../../types/analytics';
import { getProjectAiSummary } from '../../lib/api';

interface ProjectAiSummaryCardProps {
  projectId: string;
}

export const ProjectAiSummaryCard: React.FC<ProjectAiSummaryCardProps> = ({
  projectId,
}) => {
  const [summary, setSummary] = useState<ProjectAiSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadSummary = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await getProjectAiSummary(projectId);
      if (data) {
        setSummary(data);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to generate AI project summary.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      loadSummary();
    }
  }, [projectId]);

  return (
    <div className="rounded-3xl border border-blue-500/30 bg-gradient-to-br from-slate-900/90 via-slate-950/80 to-blue-950/20 p-6 backdrop-blur-md space-y-6 shadow-xl shadow-blue-950/20">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 to-violet-600 shadow-md shadow-blue-500/20">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white tracking-tight">AI Project Health & Insights</h3>
              {summary && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/40">
                  {summary.is_ai_generated ? 'Gemini 2.5 Pro' : 'Factual Deterministic'}
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400">
              Automated synthesis of milestone velocity, verification status, and financial commitments.
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={loadSummary}
          disabled={isLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-700 bg-slate-800 text-xs font-semibold text-slate-200 hover:bg-slate-700 hover:text-white disabled:opacity-50 transition-all cursor-pointer"
        >
          <RefreshCw className={`h-3 w-3 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-12 text-slate-500 space-y-3">
          <Loader2 className="h-7 w-7 animate-spin text-cyan-400" />
          <p className="text-xs font-mono">Synthesizing project records with Gemini AI...</p>
        </div>
      ) : errorMessage ? (
        <div className="rounded-xl border border-rose-500/30 bg-rose-950/30 p-4 text-xs text-rose-300">
          {errorMessage}
        </div>
      ) : summary ? (
        <div className="space-y-6">
          {/* Executive Summary Quote */}
          <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 space-y-2">
            <div className="text-[11px] font-mono font-bold uppercase tracking-wider text-cyan-400">
              Executive Summary
            </div>
            <p className="text-xs text-slate-200 leading-relaxed font-sans font-medium">
              "{summary.executive_summary}"
            </p>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              {summary.progress_assessment}
            </p>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-2.5">
              <span className="block text-[10px] font-mono text-slate-500 uppercase">Completion</span>
              <span className="font-mono text-base font-bold text-white">
                {summary.metrics.completion_percentage}%
              </span>
            </div>
            <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-2.5">
              <span className="block text-[10px] font-mono text-slate-500 uppercase">Approved</span>
              <span className="font-mono text-base font-bold text-emerald-400">
                {summary.metrics.approved_milestones} / {summary.metrics.total_milestones}
              </span>
            </div>
            <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-2.5">
              <span className="block text-[10px] font-mono text-slate-500 uppercase">In Progress</span>
              <span className="font-mono text-base font-bold text-amber-400">
                {summary.metrics.in_progress_milestones}
              </span>
            </div>
            <div className="rounded-xl border border-slate-800/80 bg-slate-900/50 p-2.5">
              <span className="block text-[10px] font-mono text-slate-500 uppercase">Settled Payments</span>
              <span className="font-mono text-base font-bold text-cyan-400">
                ${summary.metrics.completed_payments.toFixed(2)}
              </span>
            </div>
          </div>

          {/* Accomplishments, Risks, and Next Steps Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Key Accomplishments */}
            <div className="rounded-2xl border border-emerald-500/20 bg-emerald-950/10 p-4 space-y-2.5">
              <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400 font-mono">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>Accomplishments</span>
              </div>
              <ul className="space-y-1.5 text-[11px] text-slate-300">
                {summary.key_accomplishments.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-emerald-500 mt-0.5">&bull;</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Potential Risks */}
            <div className="rounded-2xl border border-amber-500/20 bg-amber-950/10 p-4 space-y-2.5">
              <div className="flex items-center gap-1.5 text-xs font-bold text-amber-400 font-mono">
                <AlertTriangle className="h-3.5 w-3.5" />
                <span>Identified Risks</span>
              </div>
              <ul className="space-y-1.5 text-[11px] text-slate-300">
                {summary.potential_risks.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-amber-500 mt-0.5">&bull;</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Recommended Next Steps */}
            <div className="rounded-2xl border border-blue-500/20 bg-blue-950/10 p-4 space-y-2.5">
              <div className="flex items-center gap-1.5 text-xs font-bold text-blue-400 font-mono">
                <Lightbulb className="h-3.5 w-3.5" />
                <span>Recommended Next Steps</span>
              </div>
              <ul className="space-y-1.5 text-[11px] text-slate-300">
                {summary.recommended_next_steps.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <ChevronRight className="h-3 w-3 text-cyan-400 mt-0.5 flex-shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

