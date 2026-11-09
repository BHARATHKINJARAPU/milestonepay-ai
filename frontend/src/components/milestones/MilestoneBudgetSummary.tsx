import React from 'react';
import { CheckCircle2, DollarSign, PieChart, ShieldAlert } from 'lucide-react';
import { Milestone } from '../../types/milestone';

interface MilestoneBudgetSummaryProps {
  totalBudget: number | string;
  currency: string;
  milestones: Milestone[];
}

export const MilestoneBudgetSummary: React.FC<MilestoneBudgetSummaryProps> = ({
  totalBudget,
  currency,
  milestones,
}) => {
  const numBudget = Number(totalBudget);
  const allocatedSum = milestones.reduce((sum, m) => sum + Number(m.amount), 0);
  const totalPercentage = milestones.reduce((sum, m) => sum + Number(m.budget_percentage), 0);

  const isExactCentMatch = Math.abs(allocatedSum - numBudget) < 0.009;

  // Segment colors for visual bar
  const segmentColors = [
    'bg-cyan-500',
    'bg-indigo-500',
    'bg-violet-500',
    'bg-emerald-500',
    'bg-amber-500',
    'bg-rose-500',
  ];

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <PieChart className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">Financial Allocation Summary</h3>
            <p className="text-xs text-slate-400">
              Deterministic cent-exact budget distribution across {milestones.length} milestone{milestones.length === 1 ? '' : 's'}
            </p>
          </div>
        </div>

        {/* Verification badge */}
        <div className="flex items-center gap-2">
          {isExactCentMatch ? (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-950/40 px-3 py-1 text-xs font-medium text-emerald-400">
              <CheckCircle2 className="h-3.5 w-3.5" />
              100% Cent-Exact Match
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-950/40 px-3 py-1 text-xs font-medium text-amber-400">
              <ShieldAlert className="h-3.5 w-3.5" />
              Allocation Discrepancy: {allocatedSum.toFixed(2)} / {numBudget.toFixed(2)}
            </span>
          )}
        </div>
      </div>

      {/* Progress Multi-segment Bar */}
      <div className="mt-5">
        <div className="h-3 w-full overflow-hidden rounded-full bg-slate-800/80 flex">
          {milestones.map((m, idx) => {
            const pct = Math.max(0, Math.min(100, Number(m.budget_percentage)));
            const colorClass = segmentColors[idx % segmentColors.length];
            return (
              <div
                key={m.id || idx}
                style={{ width: `${pct}%` }}
                className={`${colorClass} transition-all duration-300 relative group`}
                title={`M${m.sequence_number}: ${m.title} (${pct.toFixed(1)}%)`}
              />
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-400">
          {milestones.map((m, idx) => {
            const colorClass = segmentColors[idx % segmentColors.length];
            return (
              <div key={m.id || idx} className="flex items-center gap-1.5">
                <span className={`h-2.5 w-2.5 rounded-full ${colorClass}`} />
                <span className="text-slate-300 font-medium">M{m.sequence_number}:</span>
                <span className="text-slate-400 font-mono">
                  ${Number(m.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })} ({Number(m.budget_percentage).toFixed(1)}%)
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Numerical Stats Footer */}
      <div className="mt-5 grid grid-cols-2 gap-4 border-t border-slate-800/80 pt-4 sm:grid-cols-3">
        <div>
          <div className="text-xs text-slate-400">Project Total Budget</div>
          <div className="mt-1 flex items-center font-mono text-base font-bold text-white">
            <DollarSign className="h-4 w-4 text-slate-500" />
            {numBudget.toLocaleString('en-US', { minimumFractionDigits: 2 })} {currency}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-400">Milestone Total Sum</div>
          <div className="mt-1 flex items-center font-mono text-base font-bold text-cyan-400">
            <DollarSign className="h-4 w-4 text-cyan-500/70" />
            {allocatedSum.toLocaleString('en-US', { minimumFractionDigits: 2 })} {currency}
          </div>
        </div>
        <div className="col-span-2 sm:col-span-1">
          <div className="text-xs text-slate-400">Total Percentage</div>
          <div className="mt-1 font-mono text-base font-bold text-emerald-400">
            {totalPercentage.toFixed(2)}%
          </div>
        </div>
      </div>
    </div>
  );
};

