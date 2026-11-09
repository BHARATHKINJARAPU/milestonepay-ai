import React from 'react';
import {
  CheckCircle2,
  Clock,
  CreditCard,
  FileCheck,
  FileText,
  FolderKanban,
  MessageSquare,
  Sparkles,
  UserPlus,
} from 'lucide-react';
import { ProjectActivity } from '../../types/activity';

interface ActivityItemProps {
  activity: ProjectActivity;
}

export const ActivityItem: React.FC<ActivityItemProps> = ({ activity }) => {
  const getIcon = () => {
    switch (activity.activity_type) {
      case 'project_created':
        return <FolderKanban className="h-3.5 w-3.5 text-blue-400" />;
      case 'collaborator_added':
        return <UserPlus className="h-3.5 w-3.5 text-indigo-400" />;
      case 'milestone_plan_submitted':
      case 'milestone_plan_generated':
        return <FileText className="h-3.5 w-3.5 text-violet-400" />;
      case 'milestone_plan_agreed':
        return <FileCheck className="h-3.5 w-3.5 text-cyan-400" />;
      case 'revision_requested':
        return <MessageSquare className="h-3.5 w-3.5 text-amber-400" />;
      case 'deliverable_submitted':
        return <FileText className="h-3.5 w-3.5 text-purple-400" />;
      case 'ai_evaluation_completed':
        return <Sparkles className="h-3.5 w-3.5 text-amber-400" />;
      case 'milestone_approved':
        return <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />;
      case 'payment_captured':
        return <CreditCard className="h-3.5 w-3.5 text-emerald-400" />;
      default:
        return <Clock className="h-3.5 w-3.5 text-slate-400" />;
    }
  };

  const formattedTime = new Date(activity.created_at).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="relative flex items-start gap-3.5 group">
      {/* Node bullet */}
      <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-xl bg-slate-900 border border-slate-800 shadow-sm z-10">
        {getIcon()}
      </div>

      {/* Content box */}
      <div className="flex-1 min-w-0 rounded-xl border border-slate-800/80 bg-slate-950/60 p-3 hover:border-slate-700/80 transition-colors">
        <div className="flex items-center justify-between gap-2">
          <p className="text-xs font-semibold text-white truncate">{activity.title}</p>
          <span className="text-[10px] text-slate-500 font-mono whitespace-nowrap">{formattedTime}</span>
        </div>

        {activity.description && (
          <p className="mt-1 text-[11px] text-slate-300 leading-relaxed">
            {activity.description}
          </p>
        )}

        {activity.actor_name && (
          <div className="mt-1.5 flex items-center gap-1 text-[10px] text-slate-400 font-mono">
            <span>By:</span>
            <span className="text-slate-200 font-semibold">{activity.actor_name}</span>
          </div>
        )}
      </div>
    </div>
  );
};

