import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowUpRight,
  Calendar,
  CheckCircle2,
  Clock,
  CreditCard,
  DollarSign,
  FileSearch,
  GitFork,
  Send,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { Milestone } from '../../types/milestone';

interface MilestoneCardProps {
  milestone: Milestone;
  currency: string;
  projectId?: string;
  planStatus?: string;
  isFreelancer?: boolean;
  isClient?: boolean;
  isEditable?: boolean;
  onEdit?: (milestone: Milestone) => void;
}

export const MilestoneCard: React.FC<MilestoneCardProps> = ({
  milestone,
  currency,
  projectId,
  planStatus,
  isFreelancer,
  isClient,
  isEditable,
  onEdit,
}) => {
  const formattedAmount = Number(milestone.amount).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const getMilestoneStatusBadge = (status?: string) => {
    switch (status) {
      case 'in_progress':
        return {
          label: 'In Progress',
          className: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
        };
      case 'submitted':
        return {
          label: 'In Review (Deliverables Submitted)',
          className: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        };
      case 'revision_requested':
        return {
          label: 'Revision Requested',
          className: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
        };
      case 'approved':
        return {
          label: 'Milestone Approved',
          className: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        };
      case 'not_started':
      default:
        return {
          label: 'Not Started',
          className: 'bg-slate-800/80 text-slate-400 border-slate-700',
        };
    }
  };

  const statusBadge = getMilestoneStatusBadge(milestone.status);
  const isPlanAgreed = planStatus === 'agreed';
  const hasSubmissions = milestone.status && milestone.status !== 'not_started';

  return (
    <div className="relative rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm transition-all duration-200 hover:border-slate-700 hover:shadow-lg hover:shadow-cyan-950/20">
      {/* Header bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-cyan-500/10 font-mono text-sm font-semibold text-cyan-400 border border-cyan-500/20">
            {String(milestone.sequence_number).padStart(2, '0')}
          </span>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h4 className="text-lg font-semibold text-white tracking-tight">
                {milestone.title}
              </h4>
              {isPlanAgreed && (
                <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-semibold tracking-wide ${statusBadge.className}`}>
                  {statusBadge.label}
                </span>
              )}
              {milestone.payment_status === 'completed' && (
                <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/40 bg-emerald-950/60 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-400">
                  <CheckCircle2 className="h-3 w-3" />
                  Paid in Full
                </span>
              )}
            </div>
            <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-slate-400">
              <span className="inline-flex items-center gap-1">
                <Clock className="h-3.5 w-3.5 text-slate-500" />
                {milestone.estimated_duration_days} business days
              </span>
              {milestone.due_date && (
                <span className="inline-flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5 text-slate-500" />
                  Due {new Date(milestone.due_date).toLocaleDateString()}
                </span>
              )}
              {milestone.dependencies && milestone.dependencies.length > 0 && (
                <span className="inline-flex items-center gap-1 rounded bg-slate-800/80 px-2 py-0.5 text-slate-300">
                  <GitFork className="h-3 w-3 text-cyan-400" />
                  Depends on #{milestone.dependencies.join(', #')}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Budget Allocation Badge */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <div className="rounded-lg border border-cyan-500/20 bg-cyan-950/40 px-3 py-1.5 text-right">
            <div className="flex items-center justify-end gap-1 font-mono text-base font-bold text-cyan-300">
              <DollarSign className="h-4 w-4" />
              {formattedAmount} <span className="text-xs text-slate-400 font-sans">{currency}</span>
            </div>
            <div className="text-[11px] font-medium text-cyan-400/80">
              {Number(milestone.budget_percentage).toFixed(1)}% of budget
            </div>
          </div>
          {isEditable && onEdit && (
            <button
              onClick={() => onEdit(milestone)}
              className="rounded-lg border border-slate-700 bg-slate-800/80 px-2.5 py-1.5 text-xs font-medium text-slate-300 hover:border-slate-600 hover:text-white transition-colors"
            >
              Edit
            </button>
          )}
        </div>
      </div>

      {/* Description */}
      <p className="mt-4 text-sm leading-relaxed text-slate-300">
        {milestone.description}
      </p>

      {/* Deliverables & Criteria Grid */}
      <div className="mt-5 grid grid-cols-1 gap-4 pt-4 border-t border-slate-800/80 md:grid-cols-2">
        {/* Deliverables */}
        <div className="rounded-lg bg-slate-950/50 p-3.5 border border-slate-800/60">
          <h5 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-cyan-400" />
            Key Deliverables ({milestone.deliverables.length})
          </h5>
          <ul className="space-y-1.5">
            {milestone.deliverables.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-400" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Acceptance Criteria */}
        <div className="rounded-lg bg-slate-950/50 p-3.5 border border-slate-800/60">
          <h5 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            Acceptance Criteria ({milestone.acceptance_criteria.length})
          </h5>
          <ul className="space-y-1.5">
            {milestone.acceptance_criteria.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Agreed Plan Workflow Action Bar */}
      {isPlanAgreed && projectId && (
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-950/70 p-3.5">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Sparkles className="h-4 w-4 text-cyan-400" />
            <span>
              {milestone.status === 'approved'
                ? 'Milestone approved. Ready for payment release.'
                : milestone.status === 'submitted'
                ? 'Work submitted. AI evaluation ready for client review.'
                : milestone.status === 'revision_requested'
                ? 'Client requested revisions on recent submission.'
                : 'Plan agreed. Freelancer can submit deliverables & evidence.'}
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* View Submissions / AI Evaluation Link (when any submission has occurred) */}
            {hasSubmissions && (
              <Link
                to={`/projects/${projectId}/milestones/${milestone.id}/submissions/latest`}
                className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
                  isClient && milestone.status === 'submitted'
                    ? 'bg-amber-500 text-slate-950 hover:bg-amber-400 shadow-md shadow-amber-950/30'
                    : 'border border-slate-700 bg-slate-800 text-slate-200 hover:border-slate-600 hover:text-white'
                }`}
              >
                <FileSearch className="h-3.5 w-3.5" />
                {isClient && milestone.status === 'submitted'
                  ? 'Review Deliverables'
                  : 'View Submissions & AI Review'}
                <ArrowUpRight className="h-3 w-3" />
              </Link>
            )}

            {/* Client Payment Release Button */}
            {isClient && milestone.status === 'approved' && milestone.payment_status !== 'completed' && (
              <Link
                to={`/projects/${projectId}/milestones/${milestone.id}/pay`}
                className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 px-3.5 py-1.5 text-xs font-bold text-white shadow-md shadow-emerald-950/40 transition-all cursor-pointer"
              >
                <CreditCard className="h-3.5 w-3.5" />
                <span>Release Payment ({currency} {formattedAmount})</span>
              </Link>
            )}

            {/* Completed Payment Receipt Link */}
            {milestone.payment_status === 'completed' && (
              <Link
                to="/payments"
                className="inline-flex items-center gap-1.5 rounded-lg border border-emerald-500/30 bg-emerald-950/50 px-3 py-1.5 text-xs font-semibold text-emerald-300 hover:bg-emerald-950/80 transition-colors"
              >
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Payment Completed</span>
              </Link>
            )}

            {/* Freelancer Submit / Resubmit Button */}
            {isFreelancer && milestone.status !== 'approved' && (
              <Link
                to={`/projects/${projectId}/milestones/${milestone.id}/submit`}
                className="inline-flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-md shadow-cyan-950/40 hover:from-cyan-400 hover:to-indigo-500 transition-all"
              >
                <Send className="h-3.5 w-3.5" />
                {milestone.status === 'revision_requested'
                  ? 'Submit Revised Deliverables'
                  : milestone.status === 'submitted'
                  ? 'Submit New Attempt'
                  : 'Submit Deliverables'}
              </Link>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

