import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, ChevronRight, Clock } from 'lucide-react';
import { UpcomingDeadlineItem } from '../../types/analytics';

interface UpcomingDeadlinesListProps {
  deadlines: UpcomingDeadlineItem[];
}

export const UpcomingDeadlinesList: React.FC<UpcomingDeadlinesListProps> = ({
  deadlines,
}) => {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-cyan-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-white font-mono">
            Upcoming Milestone Deadlines
          </h3>
        </div>
        <span className="text-xs text-slate-500 font-mono">({deadlines.length} scheduled)</span>
      </div>

      {deadlines.length === 0 ? (
        <div className="py-8 text-center text-xs text-slate-500">
          No upcoming scheduled milestone deadlines found.
        </div>
      ) : (
        <div className="space-y-2.5">
          {deadlines.map((item) => {
            const formattedDate = item.deadline
              ? new Date(item.deadline).toLocaleDateString([], {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })
              : 'Flexible Schedule';

            return (
              <div
                key={item.milestone_id}
                className="flex items-center justify-between p-3.5 rounded-2xl border border-slate-800/80 bg-slate-950/50 hover:border-slate-700 transition-colors"
              >
                <div className="min-w-0 flex-1 pr-4">
                  <span className="text-[10px] font-mono font-bold uppercase text-slate-400 block truncate">
                    {item.project_title}
                  </span>
                  <h4 className="text-xs font-bold text-white truncate mt-0.5">{item.milestone_title}</h4>
                  <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-400">
                    <span className="flex items-center gap-1 font-mono text-cyan-400">
                      <Clock className="h-3 w-3" />
                      {formattedDate}
                    </span>
                    <span>&bull;</span>
                    <span className="font-mono text-emerald-400 font-semibold">
                      {item.currency} ${item.suggested_budget.toFixed(2)}
                    </span>
                  </div>
                </div>

                <Link
                  to={`/projects/${item.project_id}/milestones`}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-xl border border-slate-800 bg-slate-900 text-xs font-semibold text-slate-300 hover:text-white hover:border-slate-700 transition-colors"
                >
                  <span>Deliverables</span>
                  <ChevronRight className="h-3 w-3 text-slate-500" />
                </Link>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

