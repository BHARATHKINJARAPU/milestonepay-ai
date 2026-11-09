import React, { useState } from 'react';
import {
  AlertCircle,
  Check,
  CheckCircle2,
  Clock,
  FileCheck,
  Lock,
  MessageSquare,
  Send,
  Sparkles,
  Users,
} from 'lucide-react';
import { MilestonePlan } from '../../types/milestone';
import { ProjectMember } from '../../types/project';
import { User } from '../../types/auth';

interface PlanApprovalPanelProps {
  plan: MilestonePlan;
  members: ProjectMember[];
  currentUser: User | null;
  onSubmitForApproval: () => Promise<void>;
  onApprove: () => Promise<void>;
  onRequestRevision: (comment: string) => Promise<void>;
  isLoading?: boolean;
}

export const PlanApprovalPanel: React.FC<PlanApprovalPanelProps> = ({
  plan,
  members,
  currentUser,
  onSubmitForApproval,
  onApprove,
  onRequestRevision,
  isLoading,
}) => {
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [revisionComment, setRevisionComment] = useState('');
  const [submittingAction, setSubmittingAction] = useState(false);

  // Identify client and freelancer members
  const clientMember = members.find((m) => m.role === 'client');
  const freelancerMember = members.find((m) => m.role === 'freelancer');
  const hasBothRoles = Boolean(clientMember && freelancerMember);

  // Find reviews
  const clientReview = plan.reviews.find((r) => r.reviewer_role === 'client');
  const freelancerReview = plan.reviews.find((r) => r.reviewer_role === 'freelancer');

  const clientApproved = clientReview?.decision === 'approved';
  const freelancerApproved = freelancerReview?.decision === 'approved';

  const userRole = members.find((m) => m.user_id === currentUser?.id)?.role;
  const userHasApproved = plan.reviews.some(
    (r) => r.reviewer_user_id === currentUser?.id && r.decision === 'approved'
  );

  const handleSubmitForApproval = async () => {
    try {
      setSubmittingAction(true);
      await onSubmitForApproval();
    } finally {
      setSubmittingAction(false);
    }
  };

  const handleApprove = async () => {
    try {
      setSubmittingAction(true);
      await onApprove();
    } finally {
      setSubmittingAction(false);
    }
  };

  const handleConfirmRevision = async () => {
    if (!revisionComment.trim() || revisionComment.length < 5) return;
    try {
      setSubmittingAction(true);
      await onRequestRevision(revisionComment);
      setShowRevisionModal(false);
      setRevisionComment('');
    } finally {
      setSubmittingAction(false);
    }
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-6 backdrop-blur-md">
      {/* Header with Version & Status */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between pb-5 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 rounded-md bg-cyan-500/10 px-2.5 py-1 text-xs font-mono font-semibold text-cyan-400 border border-cyan-500/20">
              <FileCheck className="h-3.5 w-3.5" />
              Version {plan.version}
            </span>
            <h3 className="text-lg font-bold text-white tracking-tight">
              Bilateral Agreement Status
            </h3>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            {plan.status === 'agreed'
              ? 'This milestone plan has formal bilateral agreement and is locked.'
              : 'Both Client and Freelancer must review and explicitly approve this version before work initiates.'}
          </p>
        </div>

        {/* Status Badge */}
        <div>
          {plan.status === 'agreed' && (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/40 bg-emerald-950/60 px-3.5 py-1 text-xs font-semibold text-emerald-400 shadow-sm shadow-emerald-950">
              <Lock className="h-3.5 w-3.5" />
              Agreed & Locked
            </span>
          )}
          {plan.status === 'pending_approval' && (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/40 bg-amber-950/60 px-3.5 py-1 text-xs font-semibold text-amber-300">
              <Clock className="h-3.5 w-3.5 animate-spin" />
              Pending Mutual Approval
            </span>
          )}
          {plan.status === 'revision_requested' && (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-rose-500/40 bg-rose-950/60 px-3.5 py-1 text-xs font-semibold text-rose-300">
              <AlertCircle className="h-3.5 w-3.5" />
              Revision Requested
            </span>
          )}
          {plan.status === 'draft' && (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-slate-700 bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-300">
              <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
              Draft Proposal
            </span>
          )}
        </div>
      </div>

      {/* Two-Party Review Status Grid */}
      <div className="grid grid-cols-1 gap-4 py-5 sm:grid-cols-2">
        {/* Client Box */}
        <div
          className={`rounded-xl border p-4 transition-all ${
            clientApproved
              ? 'border-emerald-500/30 bg-emerald-950/20'
              : 'border-slate-800 bg-slate-950/50'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Client Approval
            </span>
            {clientApproved ? (
              <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-400">
                <CheckCircle2 className="h-4 w-4" />
                Approved
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-xs font-medium text-slate-500">
                <Clock className="h-3.5 w-3.5" />
                Awaiting Review
              </span>
            )}
          </div>
          <div className="mt-2.5">
            <div className="text-sm font-medium text-white">
              {clientMember?.user.full_name || 'No client registered'}
            </div>
            <div className="text-xs text-slate-400">
              {clientMember?.user.email || 'Invite a client to review'}
            </div>
          </div>
        </div>

        {/* Freelancer Box */}
        <div
          className={`rounded-xl border p-4 transition-all ${
            freelancerApproved
              ? 'border-emerald-500/30 bg-emerald-950/20'
              : 'border-slate-800 bg-slate-950/50'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Freelancer Approval
            </span>
            {freelancerApproved ? (
              <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-400">
                <CheckCircle2 className="h-4 w-4" />
                Approved
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-xs font-medium text-slate-500">
                <Clock className="h-3.5 w-3.5" />
                Awaiting Review
              </span>
            )}
          </div>
          <div className="mt-2.5">
            <div className="text-sm font-medium text-white">
              {freelancerMember?.user.full_name || 'No freelancer registered'}
            </div>
            <div className="text-xs text-slate-400">
              {freelancerMember?.user.email || 'Invite a freelancer to collaborate'}
            </div>
          </div>
        </div>
      </div>

      {/* Revisions & Feedback History */}
      {plan.reviews.some((r) => r.decision === 'changes_requested') && (
        <div className="mb-5 rounded-lg border border-rose-500/30 bg-rose-950/20 p-4">
          <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase text-rose-300 mb-2">
            <MessageSquare className="h-3.5 w-3.5" />
            Revision Feedback
          </h4>
          {plan.reviews
            .filter((r) => r.decision === 'changes_requested')
            .map((r) => (
              <div key={r.id} className="text-xs text-rose-200/90 leading-relaxed">
                <span className="font-semibold text-rose-300">{r.reviewer.full_name} ({r.reviewer_role}):</span>{' '}
                {r.comment}
              </div>
            ))}
        </div>
      )}

      {/* Action Controls */}
      <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-800">
        <div className="text-xs text-slate-400">
          {!hasBothRoles && (
            <span className="flex items-center gap-1.5 text-amber-400">
              <Users className="h-4 w-4" />
              Both a Client and a Freelancer must join before submitting for bilateral approval.
            </span>
          )}
          {hasBothRoles && plan.status === 'draft' && (
            <span>Ready for bilateral review. Review milestones carefully before submitting.</span>
          )}
          {hasBothRoles && plan.status === 'pending_approval' && userHasApproved && (
            <span className="text-cyan-400 flex items-center gap-1.5">
              <Check className="h-4 w-4" />
              You have signed this proposal version. Awaiting counterparty approval.
            </span>
          )}
          {plan.status === 'agreed' && (
            <span className="text-emerald-400 flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4" />
              Plan fully locked. Milestone deliverable submissions are enabled.
            </span>
          )}
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Submit for approval button */}
          {(plan.status === 'draft' || plan.status === 'revision_requested') && (
            <button
              onClick={handleSubmitForApproval}
              disabled={!hasBothRoles || isLoading || submittingAction}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-lg bg-cyan-600 px-5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-cyan-950/50 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <Send className="h-3.5 w-3.5" />
              {submittingAction ? 'Submitting...' : 'Submit for Mutual Approval'}
            </button>
          )}

          {/* Pending Approval actions */}
          {plan.status === 'pending_approval' && !userHasApproved && (
            <>
              <button
                onClick={() => setShowRevisionModal(true)}
                disabled={isLoading || submittingAction}
                className="w-1/2 sm:w-auto inline-flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-800/80 px-4 py-2.5 text-xs font-semibold text-slate-200 hover:border-slate-600 hover:text-white transition-all"
              >
                <MessageSquare className="h-3.5 w-3.5 text-rose-400" />
                Request Changes
              </button>
              <button
                onClick={handleApprove}
                disabled={isLoading || submittingAction}
                className="w-1/2 sm:w-auto inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-emerald-950/50 hover:bg-emerald-500 disabled:opacity-50 transition-all"
              >
                <Check className="h-3.5 w-3.5" />
                {submittingAction ? 'Approving...' : `Approve as ${userRole ? userRole.toUpperCase() : 'Member'}`}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Revision Request Modal */}
      {showRevisionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <h4 className="text-base font-semibold text-white">Request Plan Revision</h4>
            <p className="mt-1 text-xs text-slate-400">
              Provide actionable guidance or changes you require before agreeing to this milestone proposal.
            </p>
            <textarea
              rows={4}
              value={revisionComment}
              onChange={(e) => setRevisionComment(e.target.value)}
              placeholder="e.g., Please increase duration for Milestone 2 by 5 days, or split Milestone 3 into two phases..."
              className="mt-4 w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-xs text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
            />
            <div className="mt-4 flex items-center justify-end gap-3">
              <button
                onClick={() => setShowRevisionModal(false)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmRevision}
                disabled={revisionComment.trim().length < 5 || submittingAction}
                className="rounded-lg bg-rose-600 px-4 py-2 text-xs font-semibold text-white hover:bg-rose-500 disabled:opacity-50"
              >
                {submittingAction ? 'Submitting...' : 'Send Revision Request'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

