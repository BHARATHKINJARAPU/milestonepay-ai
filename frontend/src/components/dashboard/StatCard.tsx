import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badge?: string;
  colorScheme?: 'blue' | 'emerald' | 'amber' | 'violet' | 'cyan';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  colorScheme = 'blue',
}) => {
  const getSchemeClasses = () => {
    switch (colorScheme) {
      case 'emerald':
        return {
          border: 'border-emerald-500/30',
          bg: 'from-emerald-950/20 to-slate-900/60',
          iconBg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
          badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
        };
      case 'amber':
        return {
          border: 'border-amber-500/30',
          bg: 'from-amber-950/20 to-slate-900/60',
          iconBg: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
          badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
        };
      case 'violet':
        return {
          border: 'border-violet-500/30',
          bg: 'from-violet-950/20 to-slate-900/60',
          iconBg: 'bg-violet-500/20 text-violet-400 border-violet-500/30',
          badge: 'bg-violet-500/20 text-violet-300 border-violet-500/30',
        };
      case 'cyan':
        return {
          border: 'border-cyan-500/30',
          bg: 'from-cyan-950/20 to-slate-900/60',
          iconBg: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
          badge: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
        };
      case 'blue':
      default:
        return {
          border: 'border-blue-500/30',
          bg: 'from-blue-950/20 to-slate-900/60',
          iconBg: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
          badge: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
        };
    }
  };

  const scheme = getSchemeClasses();

  return (
    <div
      className={`rounded-2xl border ${scheme.border} bg-gradient-to-br ${scheme.bg} p-5 backdrop-blur-sm transition-all hover:border-slate-700 shadow-lg shadow-black/20`}
    >
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 font-mono">
          {title}
        </span>
        <div className={`flex h-8 w-8 items-center justify-center rounded-xl border ${scheme.iconBg}`}>
          <Icon className="h-4 w-4" />
        </div>
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-white font-mono">{value}</span>
        {badge && (
          <span
            className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold border ${scheme.badge}`}
          >
            {badge}
          </span>
        )}
      </div>

      {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
};
