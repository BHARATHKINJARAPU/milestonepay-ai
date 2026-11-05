import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  accent?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon: Icon,
  description,
  accent = 'from-blue-600 to-indigo-600',
}) => {
  return (
    <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl shadow-xl flex flex-col justify-between hover:border-slate-700/80 transition-all">
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono">
          {title}
        </span>
        <div className={`w-10 h-10 rounded-xl bg-gradient-to-tr ${accent} p-0.5 shadow-md shadow-blue-500/10`}>
          <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
            <Icon className="w-5 h-5 text-white" />
          </div>
        </div>
      </div>
      <div>
        <div className="text-3xl font-extrabold text-white tracking-tight">{value}</div>
        {description && <p className="text-xs text-slate-400 mt-1">{description}</p>}
      </div>
    </div>
  );
};
