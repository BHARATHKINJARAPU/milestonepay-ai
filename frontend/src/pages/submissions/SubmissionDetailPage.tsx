import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link, useOutletContext } from 'react-router-dom';
import {
  AlertCircle,
  ArrowLeft,
  Check,
  CheckCircle2,
  ExternalLink,
  History,
  Loader2,
  Lock,
  MessageSquare,
  Paperclip,
  Plus,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { DashboardHeader } from '../../components/dashboard/DashboardHeader';
import { SubmissionStatusBadge } from '../../components/submissions/SubmissionStatusBadge';
import { EvidenceFileList } from '../../components/submissions/EvidenceFileList';
import { EvaluationReport } from '../../components/evaluation/EvaluationReport';
import { useAuth } from '../../context/AuthContext';
import {
  clientApproveSubmission,
  clientRequestSubmissionRevision,
  getMilestoneSubmissions,
  getProject,
  getSubmission,
  retryDeliverableEvaluation,
} from '../../lib/api';
import { Project } from '../../types/project';
import { MilestoneSubmission } from '../../types/submission';

interface OutletContextType {
  onOpenMobileMenu: () => void;
}

export const SubmissionDetailPage: React.FC = () => {
  const { projectId, milestoneId, submissionId } = useParams<{
    projectId: string;
    milestoneId: string;
    submissionId: string;
  }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { onOpenMobileMenu } = useOutletContext<OutletContextType>();

  const [project, setProject] = useState<Project | null>(null);
  const [submission, setSubmission] = useState<MilestoneSubmission | null>(null);
  const [allAttempts, setAllAttempts] = useState<MilestoneSubmission[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Modals
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [approveComment, setApproveComment] = useState('');
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [revisionComment, setRevisionComment] = useState('');

  const loadData = async () => {
    if (!projectId || !milestoneId || !submissionId) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [projData, attemptsData] = await Promise.all([
        getProject(projectId),
        getMilestoneSubmissions(projectId, milestoneId),
      ]);
      setProject(projData);
      setAllAttempts(attemptsData.submissions);

      let targetSubId = submissionId;
      if (submissionId === 'latest') {
        if (attemptsData.submissions.length > 0) {
          targetSubId = attemptsData.submissions[0].id;
        } else {
          setErrorMessage('No deliverables submitted for this milestone yet.');
          setIsLoading(false);
          return;
        }
      }

      const subData = await getSubmission(targetSubId);
      setSubmission(subData);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to load submission review.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId, milestoneId, submissionId]);

  const isClient = project?.members.some((m) => m.user_id === user?.id && m.role === 'client');
  const isFreelancer = project?.members.some((m) => m.user_id === user?.id && m.role === 'freelancer');

  // Client approves
  const handleApprove = async () => {
    if (!submission) return;
    try {
      setIsActionLoading(true);
      const updated = await clientApproveSubmission(submission.id, approveComment.trim() || undefined);
      setSubmission(updated);
      setShowApproveModal(false);
      setApproveComment('');
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to approve milestone.');
    } finally {
      setIsActionLoading(false);
    }
  };

  // Client requests revision
  const handleRequestRevision = async () => {
    if (!submission || !revisionComment.trim() || revisionComment.length < 5) return;
    try {
      setIsActionLoading(true);
      const updated = await clientRequestSubmissionRevision(submission.id, revisionComment.trim());
      setSubmission(updated);
      setShowRevisionModal(false);
      setRevisionComment('');
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to request revision.');
    } finally {
      setIsActionLoading(false);
    }
  };

  // Retry AI evaluation
  const handleRetryEvaluation = async () => {
    if (!submission) return;
    try {
      setIsActionLoading(true);
      const updated = await retryDeliverableEvaluation(submission.id);
      setSubmission(updated);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to re-run AI evaluation.');
    } finally {
      setIsActionLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center text-slate-400 space-y-3 font-mono text-xs">
        <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
        <span>Loading submission review workspace...</span>
      </div>
    );
  }

  if (errorMessage && !submission) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-900/60 text-xs text-rose-300 flex items-center justify-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
        <Link
          to={`/projects/${projectId}/milestones`}
          className="inline-flex items-center gap-2 text-xs font-semibold text-cyan-400 hover:text-cyan-300"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Milestones</span>
        </Link>
      </div>
    );
  }

  if (!submission) return null;

  const latestAiReview = submission.ai_reviews[0];

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <DashboardHeader
        title={`Submission Attempt #${submission.attempt_number}`}
        subtitle={`Project: ${project?.title || ''}`}
        onOpenMobileMenu={onOpenMobileMenu}
      />

      {/* Meta bar & Attempt switcher */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to={`/projects/${projectId}/milestones`}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Milestone Workspace
          </Link>
          <div className="h-4 w-px bg-slate-800" />
          <SubmissionStatusBadge status={submission.status} />
        </div>

        {/* Attempt history selector */}
        {allAttempts.length > 1 && (
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-slate-400" />
            <span className="text-xs text-slate-400">Attempt:</span>
            <select
              value={submission.id}
              onChange={(e) => {
                navigate(`/projects/${projectId}/milestones/${milestoneId}/submissions/${e.target.value}`);
              }}
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs font-semibold text-slate-200 focus:border-cyan-500 focus:outline-none"
            >
              {allAttempts.map((att) => (
                <option key={att.id} value={att.id}>
                  Attempt #{att.attempt_number} ({att.status.toUpperCase()})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {errorMessage && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-950/40 p-4 text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-400" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Client Action Banner (Approve or Request Revisions) */}
      {isClient && submission.status === 'submitted' && (
        <div className="rounded-2xl border border-cyan-500/30 bg-gradient-to-r from-slate-900/90 via-slate-900/90 to-cyan-950/50 p-6 backdrop-blur-md shadow-xl shadow-cyan-950/20 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-cyan-400" />
              Client Review Decision Required
            </h4>
            <p className="mt-1 text-xs text-slate-300 leading-relaxed">
              Review the submitted work, evidence files, and the AI evaluation report below. You hold sole authority to approve the milestone or request changes.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={() => setShowRevisionModal(true)}
              disabled={isActionLoading}
              className="inline-flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-800 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:border-rose-900/60 hover:text-rose-300 hover:bg-slate-800/90 transition-all disabled:opacity-50"
            >
              <MessageSquare className="h-3.5 w-3.5 text-rose-400" />
              Request Revision
            </button>
            <button
              onClick={() => setShowApproveModal(true)}
              disabled={isActionLoading}
              className="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-emerald-950/50 hover:bg-emerald-500 transition-all disabled:opacity-50"
            >
              <Check className="h-3.5 w-3.5" />
              Approve Milestone
            </button>
          </div>
        </div>
      )}

      {/* Approved Confirmation Banner */}
      {submission.status === 'approved' && (
        <div className="rounded-2xl border border-emerald-500/30 bg-emerald-950/20 p-5 backdrop-blur-sm flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Lock className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-emerald-300">
              Milestone Deliverables Formally Approved
            </h4>
            <p className="mt-0.5 text-xs text-emerald-300/80">
              The client has signed off on this submission. Deliverables are approved and immutable.
            </p>
          </div>
        </div>
      )}

      {/* Revision Requested Banner (with CTA for Freelancer) */}
      {submission.status === 'revision_requested' && (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-5 backdrop-blur-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <MessageSquare className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-rose-300">
                Client Requested Revisions on this Attempt
              </h4>
              <p className="mt-0.5 text-xs text-rose-200/80">
                Review the client's feedback below and upload updated evidence in a new attempt.
              </p>
            </div>
          </div>

          {isFreelancer && (
            <Link
              to={`/projects/${projectId}/milestones/${milestoneId}/submit`}
              className="inline-flex items-center gap-1.5 rounded-xl bg-cyan-600 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-cyan-950 hover:bg-cyan-500 transition-all shrink-0"
            >
              <Plus className="h-3.5 w-3.5" />
              Submit Attempt #{submission.attempt_number + 1}
            </Link>
          )}
        </div>
      )}

      {/* 2-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Work Details, Evidence, and Feedback */}
        <div className="lg:col-span-5 space-y-6">
          {/* Submission Overview */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <span className="text-xs font-semibold uppercase text-slate-400 tracking-wider">
                Submission Details
              </span>
              <span className="text-[11px] font-mono text-slate-400">
                Attempt #{submission.attempt_number}
              </span>
            </div>

            <div>
              <h5 className="text-xs font-semibold uppercase text-slate-400 mb-1">
                Completed Work Description
              </h5>
              <p className="text-xs text-slate-200 leading-relaxed whitespace-pre-line bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
                {submission.description}
              </p>
            </div>

            {submission.notes && (
              <div>
                <h5 className="text-xs font-semibold uppercase text-slate-400 mb-1">
                  Implementation Notes
                </h5>
                <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
                  {submission.notes}
                </p>
              </div>
            )}

            {submission.demonstration_url && (
              <div>
                <h5 className="text-xs font-semibold uppercase text-slate-400 mb-1">
                  Live Demonstration
                </h5>
                <a
                  href={submission.demonstration_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:underline font-mono bg-cyan-950/30 border border-cyan-500/20 px-3 py-2 rounded-xl truncate max-w-full"
                >
                  <ExternalLink className="h-3.5 w-3.5 shrink-0" />
                  <span className="truncate">{submission.demonstration_url}</span>
                </a>
                <span className="block text-[11px] text-slate-500 mt-1">
                  Manual testing required. Live links are never crawled automatically.
                </span>
              </div>
            )}
          </div>

          {/* Attached Evidence Artifacts */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="text-xs font-semibold uppercase text-slate-400 tracking-wider flex items-center gap-1.5">
                <Paperclip className="h-3.5 w-3.5 text-cyan-400" />
                Attached Evidence Artifacts ({submission.evidence.length})
              </span>
            </div>
            <EvidenceFileList
              submissionId={submission.id}
              evidence={submission.evidence}
              canDelete={false}
            />
          </div>

          {/* Client Decision & Revision Comments History */}
          {submission.client_reviews && submission.client_reviews.length > 0 && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-3">
              <h4 className="text-xs font-semibold uppercase text-slate-400 tracking-wider flex items-center gap-1.5">
                <MessageSquare className="h-3.5 w-3.5 text-indigo-400" />
                Client Review History ({submission.client_reviews.length})
              </h4>
              <div className="space-y-2.5">
                {submission.client_reviews.map((cr) => (
                  <div
                    key={cr.id}
                    className={`rounded-xl border p-3.5 text-xs ${
                      cr.decision === 'approved'
                        ? 'border-emerald-500/30 bg-emerald-950/20 text-emerald-200'
                        : 'border-rose-500/30 bg-rose-950/20 text-rose-200'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5 font-semibold">
                      <span className="capitalize">{cr.decision.replace('_', ' ')}</span>
                      <span className="text-[11px] font-mono opacity-70">
                        {new Date(cr.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {cr.comment && <p className="leading-relaxed whitespace-pre-line">{cr.comment}</p>}
                    <div className="mt-2 text-[11px] opacity-70">
                      Reviewer: {cr.reviewer?.full_name || 'Client'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: AI Deliverable Evaluation Audit */}
        <div className="lg:col-span-7 space-y-6">
          {submission.ai_review_status === 'pending' && (
            <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/60 p-12 text-center space-y-3">
              <Loader2 className="mx-auto h-8 w-8 text-cyan-400 animate-spin" />
              <h4 className="text-sm font-semibold text-white">
                Gemini AI Evaluation in Progress...
              </h4>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Comparing submitted files and descriptions against exact agreed acceptance criteria.
              </p>
            </div>
          )}

          {submission.ai_review_status === 'failed' && (
            <div className="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-8 text-center space-y-3">
              <AlertCircle className="mx-auto h-8 w-8 text-rose-400" />
              <h4 className="text-sm font-semibold text-rose-300">
                Automated AI Evaluation Incomplete
              </h4>
              <p className="text-xs text-rose-200/80 max-w-sm mx-auto">
                The AI service was temporarily unavailable or encountered a format limitation. You may retry evaluation or proceed with client manual inspection.
              </p>
              <button
                type="button"
                onClick={handleRetryEvaluation}
                disabled={isActionLoading}
                className="inline-flex items-center gap-1.5 rounded-lg bg-cyan-600 px-4 py-2 text-xs font-semibold text-white hover:bg-cyan-500"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Retry AI Evaluation
              </button>
            </div>
          )}

          {submission.ai_review_status === 'completed' && latestAiReview && (
            <EvaluationReport
              review={latestAiReview}
              onRetryEvaluation={handleRetryEvaluation}
              isRetrying={isActionLoading}
            />
          )}
        </div>
      </div>

      {/* Modal: Client Approval Confirmation */}
      {showApproveModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl border border-emerald-500/30 bg-slate-900 p-6 shadow-2xl">
            <h4 className="text-base font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              Approve Milestone Deliverables
            </h4>
            <p className="mt-2 text-xs text-slate-300 leading-relaxed">
              Are you sure you want to approve this milestone? This marks the deliverables complete and finalizes this phase.
            </p>

            <div className="mt-4">
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Approval Note (Optional)
              </label>
              <textarea
                rows={3}
                value={approveComment}
                onChange={(e) => setApproveComment(e.target.value)}
                placeholder="e.g., Deliverables verified. Ready for next milestone."
                className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div className="mt-5 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowApproveModal(false)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleApprove}
                disabled={isActionLoading}
                className="rounded-lg bg-emerald-600 px-5 py-2 text-xs font-semibold text-white hover:bg-emerald-500 shadow-lg shadow-emerald-950 disabled:opacity-50"
              >
                {isActionLoading ? 'Approving...' : 'Confirm Approval'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Client Revision Request */}
      {showRevisionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl border border-rose-500/30 bg-slate-900 p-6 shadow-2xl">
            <h4 className="text-base font-bold text-white flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-rose-400" />
              Request Deliverable Revisions
            </h4>
            <p className="mt-2 text-xs text-slate-300 leading-relaxed">
              Describe the specific deficiencies or items that need remediation before this milestone can be approved.
            </p>

            <div className="mt-4">
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Revision Feedback (Required, min 5 chars)
              </label>
              <textarea
                rows={4}
                required
                value={revisionComment}
                onChange={(e) => setRevisionComment(e.target.value)}
                placeholder="e.g., Please provide unit test execution logs and fix the header alignment on mobile view..."
                className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-xs text-white focus:border-rose-500 focus:outline-none"
              />
            </div>

            <div className="mt-5 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowRevisionModal(false)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleRequestRevision}
                disabled={isActionLoading || revisionComment.trim().length < 5}
                className="rounded-lg bg-rose-600 px-5 py-2 text-xs font-semibold text-white hover:bg-rose-500 shadow-lg shadow-rose-950 disabled:opacity-50"
              >
                {isActionLoading ? 'Submitting...' : 'Send Revision Request'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
