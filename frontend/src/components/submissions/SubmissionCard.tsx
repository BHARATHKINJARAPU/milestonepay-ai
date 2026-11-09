import React from 'react';
import { Link } from 'react-router-dom';
import {
  Bot,
  Calendar,
  ChevronRight,
  ExternalLink,
  Paperclip,
  Sparkles,
  User,
} from 'lucide-react';
import { MilestoneSubmission } from '../../types/submission';
import { SubmissionStatusBadge } from './SubmissionStatusBadge';

interface SubmissionCardProps {
  submission: MilestoneSubmission;
  projectId: string;
  milestoneId: string;
}

export const SubmissionCard: React.FC<SubmissionCardProps> = ({
  submission,
  projectId,
  milestoneId,
}) => {
  const latestAiReview = submission.ai_reviews[0];

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm transition-all hover:border-slate-700 hover:shadow-lg hover:shadow-cyan-950/20">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-cyan-500/10 font-mono text-xs font-bold text-cyan-400 border border-cyan-500/20">
            #{submission.attempt_number}
          </span>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h4 className="text-sm font-bold text-white">
                Submission Attempt #{submission.attempt_number}
              </h4>
              <SubmissionStatusBadge status={submission.status} />
            </div>

            <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-slate-400">
              <span className="inline-flex items-center gap-1">
                <User className="h-3 w-3 text-slate-500" />
                {submission.submitted_by?.full_name || 'Freelancer'}
              </span>
              <span className="inline-flex items-center gap-1">
                <Calendar className="h-3 w-3 text-slate-500" />
                {submission.submitted_at
                  ? new Date(submission.submitted_at).toLocaleDateString()
                  : `Drafted ${new Date(submission.created_at).toLocaleDateString()}`}
              </span>
              <span className="inline-flex items-center gap-1 text-slate-400">
                <Paperclip className="h-3 w-3 text-cyan-400" />
                {submission.evidence.length} evidence file{submission.evidence.length === 1 ? '' : 's'}
              </span>
            </div>
          </div>
        </div>

        {/* AI Evaluation Status Pill */}
        {submission.status !== 'draft' && (
          <div>
            {submission.ai_review_status === 'completed' && (
              <span className="inline-flex items-center gap-1 rounded-full border border-indigo-500/30 bg-indigo-950/40 px-2.5 py-0.5 text-[11px] font-semibold text-indigo-300">
                <Sparkles className="h-3 w-3 text-cyan-400" />
                AI Evaluated
              </span>
            )}
            {submission.ai_review_status === 'pending' && (
              <span className="inline-flex items-center gap-1 rounded-full border border-amber-500/30 bg-amber-950/40 px-2.5 py-0.5 text-[11px] font-semibold text-amber-300 animate-pulse">
                <Bot className="h-3 w-3" />
                AI Evaluating...
              </span>
            )}
            {submission.ai_review_status === 'failed' && (
              <span className="inline-flex items-center gap-1 rounded-full border border-rose-500/30 bg-rose-950/40 px-2.5 py-0.5 text-[11px] font-semibold text-rose-300">
                AI Review Incomplete
              </span>
            )}
          </div>
        )}
      </div>

      {/* Description Snippet */}
      <p className="mt-3 text-xs text-slate-300 leading-relaxed line-clamp-2">
        {submission.description}
      </p>

      {/* Demo URL preview if present */}
      {submission.demonstration_url && (
        <div className="mt-2 text-[11px] text-slate-400 flex items-center gap-1.5 font-mono">
          <span className="text-slate-500">Live Demo:</span>
          <a
            href={submission.demonstration_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-cyan-400 hover:underline flex items-center gap-1 truncate max-w-xs"
          >
            {submission.demonstration_url}
            <ExternalLink className="h-2.5 w-2.5" />
          </a>
        </div>
      )}

      {/* Footer Navigation */}
      <div className="mt-4 flex items-center justify-between border-t border-slate-800/80 pt-3">
        <div className="text-[11px] text-slate-500 font-mono">
          {latestAiReview && latestAiReview.evaluation_results ? (
            <span>
              {latestAiReview.evaluation_results.filter((r) => r.status === 'met').length} of{' '}
              {latestAiReview.evaluation_results.length} criteria met
            </span>
          ) : (
            <span>{submission.status === 'draft' ? 'Awaiting submission' : 'Evaluation pending'}</span>
          )}
        </div>

        <Link
          to={`/projects/${projectId}/milestones/${milestoneId}/submissions/${submission.id}`}
          className="inline-flex items-center gap-1 text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          <span>View Submission & Audit Report</span>
          <ChevronRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </div>
  );
};

