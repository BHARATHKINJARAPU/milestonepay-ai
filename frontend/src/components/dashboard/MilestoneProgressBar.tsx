import React from 'react';
import { DashboardMilestonesSummary } from '../../types/analytics';

interface MilestoneProgressBarProps {
  summary: DashboardMilestonesSummary;
}

export const MilestoneProgressBar: React.FC<MilestoneProgressBarProps> = ({
  summary,
}) => {
  const total = summary.total || 1;
  const approvedPct = Math.round((summary.approved / total) * 100);
  const submittedPct = Math.round((summary.submitted / total) * 100);
  const inProgressPct = Math.round((summary.in_progress / total) * 100);
  const revisionPct = Math.round((summary.revision_requested / total) * 100);

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <h3 className="text-sm font-bold uppercase tracking-wider text-white font-mono">
          Milestone Execution Breakdown
        </h3>
        <span className="text-xs font-mono text-cyan-400">
          {summary.approved} / {summary.total} Approved ({approvedPct}%)
        </span>
      </div>

      {/* Multi-segment Progress Bar */}
      <div className="h-3.5 w-full overflow-hidden rounded-full bg-slate-950 flex p-0.5 border border-slate-800">
        {summary.approved > 0 && (
          <div
            style={{ width: `${approvedPct}%` }}
            title={`Approved: ${summary.approved}`}
            className="h-full bg-emerald-500 rounded-l-full transition-all"
          />
        )}
        {summary.submitted > 0 && (
          <div
            style={{ width: `${submittedPct}%` }}
            title={`Submitted / In Review: ${summary.submitted}`}
            className="h-full bg-blue-500 transition-all"
          />
        )}
        {summary.revision_requested > 0 && (
          <div
            style={{ width: `${revisionPct}%` }}
            title={`Revision Requested: ${summary.revision_requested}`}
            className="h-full bg-amber-500 transition-all"
          />
        )}
        {summary.in_progress > 0 && (
          <div
            style={{ width: `${inProgressPct}%` }}
            title={`In Progress: ${summary.in_progress}`}
            className="h-full bg-cyan-400 transition-all"
          />
        )}
      </div>

      {/* Legend */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2 text-xs">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 flex-shrink-0" />
          <span className="text-slate-400">Approved:</span>
          <span className="font-mono font-bold text-white">{summary.approved}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-blue-500 flex-shrink-0" />
          <span className="text-slate-400">Submitted:</span>
          <span className="font-mono font-bold text-white">{summary.submitted}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-amber-500 flex-shrink-0" />
          <span className="text-slate-400">Revisions:</span>
          <span className="font-mono font-bold text-white">{summary.revision_requested}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-cyan-400 flex-shrink-0" />
          <span className="text-slate-400">In Progress:</span>
          <span className="font-mono font-bold text-white">{summary.in_progress}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-slate-700 flex-shrink-0" />
          <span className="text-slate-400">Not Started:</span>
          <span className="font-mono font-bold text-white">{summary.not_started}</span>
        </div>
      </div>
    </div>
  );
};

