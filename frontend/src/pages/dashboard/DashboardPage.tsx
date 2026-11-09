import React, { useEffect, useState } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Briefcase,
  CheckCircle2,
  Clock,
  FolderKanban,
  Loader2,
  Plus,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { DashboardHeader } from '../../components/dashboard/DashboardHeader';
import { StatCard } from '../../components/dashboard/StatCard';
import { FinancialOverviewCard } from '../../components/dashboard/FinancialOverviewCard';
import { ReviewCenterList } from '../../components/dashboard/ReviewCenterList';
import { UpcomingDeadlinesList } from '../../components/dashboard/UpcomingDeadlinesList';
import { MilestoneProgressBar } from '../../components/dashboard/MilestoneProgressBar';
import { PaymentTrendChart } from '../../components/dashboard/PaymentTrendChart';
import { CollaboratorList } from '../../components/dashboard/CollaboratorList';
import { ProjectCard } from '../../components/projects/ProjectCard';
import { useAuth } from '../../context/AuthContext';
import { getDashboardAnalytics, getPaymentAnalytics, getProjects } from '../../lib/api';
import { DashboardAnalytics, PaymentAnalytics } from '../../types/analytics';
import { Project } from '../../types/project';

interface OutletContextType {
  onOpenMobileMenu: () => void;
}

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { onOpenMobileMenu } = useOutletContext<OutletContextType>();

  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [paymentAnalytics, setPaymentAnalytics] = useState<PaymentAnalytics | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const isClient = user?.account_type === 'client';

  const loadData = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [analyticsData, payAnalyticsData, projectsData] = await Promise.all([
        getDashboardAnalytics(),
        getPaymentAnalytics(),
        getProjects(),
      ]);
      setAnalytics(analyticsData);
      setPaymentAnalytics(payAnalyticsData);
      setProjects(projectsData);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to load dashboard data.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const todayStr = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return (
    <div className="space-y-8 pb-16">
      <DashboardHeader
        title={`${isClient ? 'Client' : 'Freelancer'} Workspace`}
        subtitle={`Welcome back, ${user?.full_name || 'Partner'}. Today is ${todayStr}.`}
        onOpenMobileMenu={onOpenMobileMenu}
      />

      {/* Top Welcome / Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-blue-500/30 bg-gradient-to-r from-blue-950/40 via-slate-900 to-indigo-950/30 p-6 sm:p-8 backdrop-blur-md shadow-xl shadow-blue-950/10">
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/40">
              <Sparkles className="h-3 w-3" />
              <span>MilestonePay AI &bull; {isClient ? 'Enterprise Client Suite' : 'Autonomous Freelancer Hub'}</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
              {isClient
                ? 'Review deliverables, inspect AI audits & release milestone payments.'
                : 'Structure project deliverables, track milestones & get paid transparently.'}
            </h2>
            <p className="text-xs text-slate-300 leading-relaxed">
              {isClient
                ? 'Your client dashboard aggregates active project commitments, milestone review queues, and verified PayPal Sandbox captures in one place.'
                : 'Your freelancer dashboard gives you clear visibility into agreed milestone deliverables, upcoming deadlines, and platform settlement status.'}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/projects/new"
              className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-cyan-950/50 transition-all cursor-pointer"
            >
              <Plus className="h-4 w-4" />
              <span>Create Project</span>
            </Link>

            <button
              type="button"
              onClick={loadData}
              disabled={isLoading}
              title="Refresh Dashboard"
              className="flex items-center justify-center h-10 w-10 rounded-xl border border-slate-700 bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors cursor-pointer"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24 text-slate-500 space-y-3">
          <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
          <p className="text-xs font-mono">Aggregating PostgreSQL project and financial records...</p>
        </div>
      ) : errorMessage ? (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-6 text-center text-xs text-rose-300 flex items-center justify-center gap-2">
          <AlertCircle className="h-4 w-4" />
          <span>{errorMessage}</span>
        </div>
      ) : analytics ? (
        <div className="space-y-8">
          {/* Top Key Statistics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Total Projects"
              value={analytics.projects.total}
              subtitle={`${analytics.projects.active} active workspace(s)`}
              icon={FolderKanban}
              badge={analytics.projects.completed > 0 ? `${analytics.projects.completed} done` : undefined}
              colorScheme="blue"
            />
            <StatCard
              title="Approved Milestones"
              value={analytics.milestones.approved}
              subtitle={`Out of ${analytics.milestones.total} total milestones`}
              icon={CheckCircle2}
              badge={`${Math.round((analytics.milestones.approved / (analytics.milestones.total || 1)) * 100)}%`}
              colorScheme="emerald"
            />
            <StatCard
              title={isClient ? 'Actionable Reviews' : 'Milestones In Progress'}
              value={isClient ? analytics.projects.attention_needed : analytics.milestones.in_progress}
              subtitle={isClient ? 'Submissions or plans awaiting client review' : 'Active milestone deliverables'}
              icon={isClient ? AlertTriangle : Clock}
              colorScheme="amber"
            />
            <StatCard
              title="Platform Settlements"
              value={`$${(
                (analytics.payments.completed_paypal_by_currency[0]?.amount || 0) +
                (analytics.payments.completed_mock_by_currency[0]?.amount || 0)
              ).toFixed(2)}`}
              subtitle={`${analytics.payments.completed_count} verified settlement(s)`}
              icon={ShieldCheck}
              badge={analytics.payments.completed_paypal_by_currency[0]?.amount ? 'PayPal' : 'Mock'}
              colorScheme="cyan"
            />
          </div>

          {/* Review Center for Client OR Upcoming Deadlines for Freelancer */}
          {isClient ? (
            <ReviewCenterList items={analytics.review_center} />
          ) : (
            <UpcomingDeadlinesList deadlines={analytics.upcoming_deadlines} />
          )}

          {/* Financial Commitments & Settlements */}
          <FinancialOverviewCard payments={analytics.payments} role={analytics.role} />

          {/* Milestone Execution Breakdown & Settlement Trends */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <MilestoneProgressBar summary={analytics.milestones} />
            <PaymentTrendChart trends={paymentAnalytics?.trends || []} />
          </div>

          {/* Collaborator Overview & Recent Projects Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <CollaboratorList collaborators={analytics.collaborators} role={analytics.role} />
            </div>

            <div className="lg:col-span-2 rounded-3xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Briefcase className="h-4 w-4 text-cyan-400" />
                  <h3 className="text-sm font-bold uppercase tracking-wider text-white font-mono">
                    Recent Projects
                  </h3>
                </div>
                <Link
                  to="/projects"
                  className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
                >
                  <span>View all</span>
                  <ArrowRight className="h-3 w-3" />
                </Link>
              </div>

              {projects.length === 0 ? (
                <div className="py-10 text-center text-xs text-slate-500">
                  No projects created yet.{' '}
                  <Link to="/projects/new" className="text-cyan-400 hover:underline">
                    Create your first project
                  </Link>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {projects.slice(0, 4).map((p) => (
                    <ProjectCard key={p.id} project={p} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
