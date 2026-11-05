import React, { useEffect, useState } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import { 
  FolderKanban, 
  CheckCircle2, 
  Clock, 
  DollarSign, 
  Plus, 
  ArrowRight, 
  Calendar, 
  AlertCircle,
  Sparkles
} from 'lucide-react';
import { DashboardHeader } from '../../components/dashboard/DashboardHeader';
import { StatCard } from '../../components/dashboard/StatCard';
import { ProjectCard } from '../../components/projects/ProjectCard';
import { useAuth } from '../../context/AuthContext';
import { getProjects } from '../../lib/api';
import { Project } from '../../types/project';

interface OutletContextType {
  onOpenMobileMenu: () => void;
}

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { onOpenMobileMenu } = useOutletContext<OutletContextType>();

  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const data = await getProjects();
        setProjects(data);
      } catch (err: unknown) {
        setErrorMessage(err instanceof Error ? err.message : 'Failed to load projects');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const isClient = user?.account_type === 'client';

  // Computed metrics
  const activeCount = projects.filter(p => p.status === 'active').length;
  const completedCount = projects.filter(p => p.status === 'completed').length;
  const totalBudget = projects.reduce((acc, p) => acc + Number(p.budget_amount || 0), 0);

  // Projects with upcoming deadlines
  const upcomingDeadlines = projects
    .filter(p => p.deadline && p.status !== 'completed' && p.status !== 'archived')
    .sort((a, b) => (a.deadline! > b.deadline! ? 1 : -1))
    .slice(0, 3);

  return (
    <div>
      <DashboardHeader
        title={isClient ? "Client Portal" : "Freelancer Workspace"}
        subtitle={`Welcome back, ${user?.full_name || 'User'}`}
        onOpenMobileMenu={onOpenMobileMenu}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8 space-y-8">
        {errorMessage && (
          <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-900/60 text-xs text-rose-300 flex items-center gap-3">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Metric Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title={isClient ? "Projects Created" : "Total Projects"}
            value={projects.length}
            icon={FolderKanban}
            description="All scoped projects"
            accent="from-blue-600 to-indigo-600"
          />
          <StatCard
            title="In Progress"
            value={activeCount}
            icon={Clock}
            description="Active deliverable milestones"
            accent="from-emerald-600 to-teal-600"
          />
          <StatCard
            title="Completed"
            value={completedCount}
            icon={CheckCircle2}
            description="Verified & approved projects"
            accent="from-indigo-600 to-violet-600"
          />
          <StatCard
            title="Total Volume"
            value={`$${totalBudget.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`}
            icon={DollarSign}
            description="Aggregate contract value"
            accent="from-violet-600 to-fuchsia-600"
          />
        </div>

        {/* 2-Column Section: Project List & Upcoming Deadlines / Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Main Column: Recent Projects */}
          <div className="lg:col-span-8 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white tracking-tight">Active & Recent Projects</h2>
                <p className="text-xs text-slate-400">Direct overview of your current milestone engagements</p>
              </div>
              {projects.length > 0 && (
                <Link
                  to="/projects"
                  className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1 transition-colors"
                >
                  <span>View All ({projects.length})</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              )}
            </div>

            {isLoading ? (
              <div className="p-12 text-center rounded-3xl bg-slate-900/40 border border-slate-800 text-slate-500 text-sm font-mono">
                Loading workspace projects...
              </div>
            ) : projects.length === 0 ? (
              /* Meaningful Empty State */
              <div className="p-10 rounded-3xl bg-slate-900/50 border border-slate-800 text-center space-y-4">
                <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 mx-auto flex items-center justify-center text-blue-400">
                  <FolderKanban className="w-6 h-6" />
                </div>
                <div className="max-w-sm mx-auto space-y-1">
                  <h3 className="text-base font-semibold text-white">No projects found</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {isClient
                      ? "Get started by creating your first project brief and adding a registered freelancer to collaborate."
                      : "You are not currently linked to any projects. Create a new project scope or ask your client to add you."}
                  </p>
                </div>
                <Link
                  to="/projects/new"
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all"
                >
                  <Plus className="w-4 h-4" />
                  <span>Create First Project</span>
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {projects.slice(0, 4).map(project => (
                  <ProjectCard key={project.id} project={project} />
                ))}
              </div>
            )}
          </div>

          {/* Side Column: Deadlines & Activity */}
          <div className="lg:col-span-4 space-y-6">
            {/* Upcoming Deadlines Widget */}
            <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2 text-white text-sm font-semibold">
                  <Calendar className="w-4 h-4 text-blue-400" />
                  <span>Upcoming Deadlines</span>
                </div>
                <span className="text-[10px] font-mono text-slate-500 uppercase">Target</span>
              </div>

              {upcomingDeadlines.length === 0 ? (
                <p className="text-xs text-slate-500 italic py-2">
                  No upcoming deadlines scheduled across current projects.
                </p>
              ) : (
                <div className="space-y-3">
                  {upcomingDeadlines.map(p => (
                    <Link
                      key={p.id}
                      to={`/projects/${p.id}`}
                      className="block p-3 rounded-2xl bg-slate-950/70 border border-slate-800/80 hover:border-blue-500/30 transition-all group"
                    >
                      <h4 className="text-xs font-semibold text-white group-hover:text-blue-400 transition-colors line-clamp-1">
                        {p.title}
                      </h4>
                      <div className="mt-1 flex items-center justify-between text-[11px] font-mono text-slate-400">
                        <span>{p.currency} {Number(p.budget_amount).toLocaleString()}</span>
                        <span className="text-amber-400 font-medium">{p.deadline}</span>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>

            {/* Architecture / Next Phase Roadmap Card */}
            <div className="p-6 rounded-3xl bg-gradient-to-br from-slate-900 to-indigo-950/40 border border-indigo-900/40 space-y-3">
              <div className="flex items-center gap-2 text-indigo-300 text-xs font-semibold uppercase tracking-wider font-mono">
                <Sparkles className="w-4 h-4" />
                <span>Next Milestone AI Preview</span>
              </div>
              <h4 className="text-sm font-bold text-white">AI Milestone Breakdown (Day 3)</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                In upcoming phases, you will be able to click <strong className="text-slate-300">"Generate Milestones"</strong> on any project to decompose unstructured briefs into verified milestones and PayPal escrow checkouts.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
