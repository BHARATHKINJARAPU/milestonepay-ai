import React from 'react';
import { Calendar, CheckCircle2, Clock, DollarSign, GitCommit } from 'lucide-react';
import { Milestone } from '../../types/milestone';

interface MilestoneTimelineProps {
  milestones: Milestone[];
  currency: string;
}

export const MilestoneTimeline: React.FC<MilestoneTimelineProps> = ({ milestones, currency }) => {
  const sorted = [...milestones].sort((a, b) => a.sequence_number - b.sequence_number);

  return (
    <div className="relative rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
      <div className="flex items-center gap-2 mb-6">
        <GitCommit className="h-5 w-5 text-cyan-400" />
        <h3 className="text-base font-semibold text-white">Project Roadmap Timeline</h3>
      </div>

      <div className="relative pl-6 before:absolute before:bottom-3 before:left-[11px] before:top-3 before:w-0.5 before:bg-gradient-to-b before:from-cyan-500 before:via-indigo-500 before:to-slate-800">
        {sorted.map((m, idx) => (
          <div key={m.id || idx} className="relative pb-8 last:pb-2">
            {/* Timeline node icon */}
            <span className="absolute -left-[30px] top-1.5 flex h-6 w-6 items-center justify-center rounded-full border-2 border-slate-900 bg-cyan-500 text-[10px] font-bold text-slate-950 shadow-md shadow-cyan-500/20">
              {m.sequence_number}
            </span>

            {/* Content card */}
            <div className="rounded-lg border border-slate-800/80 bg-slate-950/40 p-4 transition-all hover:border-slate-700">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h4 className="text-sm font-semibold text-white">{m.title}</h4>
                  <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-slate-400">
                    <span className="inline-flex items-center gap-1">
                      <Clock className="h-3 w-3 text-slate-500" />
                      {m.estimated_duration_days} days
                    </span>
                    {m.start_date && m.due_date && (
                      <span className="inline-flex items-center gap-1">
                        <Calendar className="h-3 w-3 text-slate-500" />
                        {new Date(m.start_date).toLocaleDateString()} &rarr; {new Date(m.due_date).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 text-right">
                  <span className="font-mono text-sm font-bold text-cyan-400 flex items-center">
                    <DollarSign className="h-3.5 w-3.5" />
                    {Number(m.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })} {currency}
                  </span>
                  <span className="rounded bg-slate-800 px-2 py-0.5 text-[11px] text-slate-300">
                    {Number(m.budget_percentage).toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Deliverable preview badges */}
              <div className="mt-3 flex flex-wrap gap-2">
                {m.deliverables.slice(0, 3).map((d, dIdx) => (
                  <span
                    key={dIdx}
                    className="inline-flex items-center gap-1 rounded bg-slate-900 px-2 py-0.5 text-[11px] text-slate-300 border border-slate-800"
                  >
                    <CheckCircle2 className="h-3 w-3 text-cyan-400" />
                    {d}
                  </span>
                ))}
                {m.deliverables.length > 3 && (
                  <span className="text-[11px] text-slate-500 self-center">
                    +{m.deliverables.length - 3} more
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

