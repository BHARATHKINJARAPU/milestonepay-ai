import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, ArrowUpRight } from 'lucide-react';
import { Project, ProjectStatus } from '../../types/project';
import { useAuth } from '../../context/AuthContext';

interface ProjectCardProps {
  project: Project;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  const { user } = useAuth();

  const myMembership = project.members.find(m => m.user_id === user?.id);
  const otherMember = project.members.find(m => m.user_id !== user?.id);

  const getStatusColor = (status: ProjectStatus) => {
    switch (status) {
      case 'active':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'completed':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'archived':
        return 'text-slate-400 bg-slate-800 border-slate-700';
      case 'draft':
      default:
        return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    }
  };

  return (
    <div className="rounded-3xl p-6 bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all duration-200 flex flex-col justify-between group hover:bg-slate-900/90 hover:shadow-xl hover:shadow-blue-900/10">
      <div>
        {/* Header: Status and Role */}
        <div className="flex items-center justify-between gap-2 mb-4">
          <span className={`text-[11px] font-mono px-2.5 py-1 rounded-full uppercase tracking-wider font-semibold border ${getStatusColor(project.status)}`}>
            {project.status}
          </span>
          {myMembership && (
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700 capitalize">
              Role: {myMembership.role}
            </span>
          )}
        </div>

        {/* Title */}
        <Link to={`/projects/${project.id}`} className="group-hover:text-blue-400 transition-colors">
          <h3 className="text-lg font-bold text-white line-clamp-1 mb-2">
            {project.title}
          </h3>
        </Link>

        {/* Description snippet */}
        <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-5">
          {project.description}
        </p>

        {/* Details row: Budget & Deadline */}
        <div className="grid grid-cols-2 gap-2 p-3 rounded-2xl bg-slate-950/60 border border-slate-800/80 text-xs mb-4">
          <div className="space-y-0.5">
            <span className="text-[10px] text-slate-500 uppercase tracking-wider font-mono">Total Budget</span>
            <div className="font-semibold text-white flex items-center gap-1">
              <span>{project.currency}</span>
              <span>{Number(project.budget_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
            </div>
          </div>
          <div className="space-y-0.5">
            <span className="text-[10px] text-slate-500 uppercase tracking-wider font-mono">Target Date</span>
            <div className="text-slate-300 flex items-center gap-1.5 truncate">
              <Calendar className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              <span className="truncate">{project.deadline || 'Flexible'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer: Collaborator info & view action */}
      <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 text-slate-400 min-w-0">
          <Users className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          {otherMember ? (
            <span className="truncate text-slate-300">{otherMember.user.full_name} ({otherMember.role})</span>
          ) : (
            <span className="text-amber-400/90 text-[11px] font-mono">Awaiting Collaborator</span>
          )}
        </div>

        <Link
          to={`/projects/${project.id}`}
          className="text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 transition-colors shrink-0"
        >
          <span>View</span>
          <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
        </Link>
      </div>
    </div>
  );
};
