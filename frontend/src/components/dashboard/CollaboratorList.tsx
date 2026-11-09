import React from 'react';
import { Users } from 'lucide-react';
import { CollaboratorOverviewItem } from '../../types/analytics';

interface CollaboratorListProps {
  collaborators: CollaboratorOverviewItem[];
  role: 'client' | 'freelancer';
}

export const CollaboratorList: React.FC<CollaboratorListProps> = ({
  collaborators,
  role,
}) => {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-violet-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-white font-mono">
            {role === 'client' ? 'Active Freelancer Partners' : 'Client Collaborators'}
          </h3>
        </div>
        <span className="text-xs text-slate-500 font-mono">({collaborators.length})</span>
      </div>

      {collaborators.length === 0 ? (
        <div className="py-8 text-center text-xs text-slate-500">
          No collaborating partners linked to your projects yet.
        </div>
      ) : (
        <div className="space-y-3">
          {collaborators.map((c) => (
            <div
              key={c.user_id}
              className="flex items-center justify-between p-3.5 rounded-2xl border border-slate-800/80 bg-slate-950/40 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-500/20 border border-violet-500/30 text-violet-300 font-bold text-xs uppercase">
                  {c.name.slice(0, 2)}
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white">{c.name}</h4>
                  <p className="text-[11px] text-slate-400">{c.email}</p>
                </div>
              </div>

              <div className="text-right">
                <span className="text-xs font-mono font-bold text-slate-200">
                  {c.project_count} {c.project_count === 1 ? 'project' : 'projects'}
                </span>
                {c.latest_project_title && (
                  <span className="block text-[10px] text-slate-500 truncate max-w-32">
                    {c.latest_project_title}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

