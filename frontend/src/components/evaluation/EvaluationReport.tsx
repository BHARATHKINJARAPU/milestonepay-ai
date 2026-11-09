import React from 'react';
import { Bot, CheckCircle2, FileSearch, Sparkles } from 'lucide-react';
import { AISubmissionReview } from '../../types/submission';
import { CriterionEvaluationCard } from './CriterionEvaluationCard';
import { IdentifiedGaps } from './IdentifiedGaps';
import { RevisionRecommendations } from './RevisionRecommendations';
import { EvidenceLimitations } from './EvidenceLimitations';

interface EvaluationReportProps {
  review: AISubmissionReview;
  onRetryEvaluation?: () => Promise<void>;
  isRetrying?: boolean;
}

export const EvaluationReport: React.FC<EvaluationReportProps> = ({
  review,
  onRetryEvaluation,
  isRetrying,
}) => {
  const evaluations = review.evaluation_results || [];
  const metCount = evaluations.filter((e) => e.status === 'met').length;
  const partialCount = evaluations.filter((e) => e.status === 'partially_met').length;
  const missingCount = evaluations.filter(
    (e) => e.status === 'not_demonstrated' || e.status === 'unable_to_assess'
  ).length;

  return (
    <div className="rounded-2xl border border-indigo-500/20 bg-slate-900/80 p-6 backdrop-blur-md space-y-6">
      {/* Header bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500/20 to-indigo-500/20 border border-cyan-500/30 text-cyan-400">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white tracking-tight">
                Gemini AI Deliverable Evaluation Audit
              </h3>
              <span className="flex items-center gap-1 rounded bg-indigo-500/10 px-2 py-0.5 font-mono text-[11px] font-semibold text-indigo-300 border border-indigo-500/20">
                <Sparkles className="h-3 w-3 text-cyan-400" />
                Review v{review.review_version}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Evaluated using {review.model_name || 'Gemini 2.5 Flash'} against exact agreed acceptance criteria
            </p>
          </div>
        </div>

        {onRetryEvaluation && (
          <button
            type="button"
            onClick={onRetryEvaluation}
            disabled={isRetrying}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white transition-colors disabled:opacity-50"
          >
            <FileSearch className="h-3.5 w-3.5" />
            <span>{isRetrying ? 'Re-evaluating...' : 'Re-Run Audit'}</span>
          </button>
        )}
      </div>

      {/* Advisory Notice Banner */}
      <div className="rounded-xl border border-cyan-500/20 bg-cyan-950/20 p-3.5 text-xs text-cyan-300/90 leading-relaxed">
        <strong className="text-cyan-200">Advisory Notice:</strong> This AI audit analyzes provided evidence artifacts against agreed criteria. It does NOT authorize payments or replace client review. Final approval rests exclusively with the client.
      </div>

      {/* Summary Scorecard */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-950/20 p-3.5 text-center">
          <div className="text-lg font-bold text-emerald-400 font-mono">{metCount}</div>
          <div className="text-[11px] text-emerald-300/80 uppercase font-semibold mt-0.5">
            Criteria Met
          </div>
        </div>
        <div className="rounded-xl border border-amber-500/20 bg-amber-950/20 p-3.5 text-center">
          <div className="text-lg font-bold text-amber-400 font-mono">{partialCount}</div>
          <div className="text-[11px] text-amber-300/80 uppercase font-semibold mt-0.5">
            Partially Satisfied
          </div>
        </div>
        <div className="rounded-xl border border-rose-500/20 bg-rose-950/20 p-3.5 text-center">
          <div className="text-lg font-bold text-rose-400 font-mono">{missingCount}</div>
          <div className="text-[11px] text-rose-300/80 uppercase font-semibold mt-0.5">
            Not Demonstrated
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
          Executive Evaluation Summary
        </h4>
        <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">
          {review.overall_summary}
        </p>
      </div>

      {/* Individual Criteria Evaluations */}
      <div className="space-y-3">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <CheckCircle2 className="h-4 w-4 text-cyan-400" />
          Criterion-by-Criterion Audit ({evaluations.length})
        </h4>
        <div className="space-y-3">
          {evaluations.map((item) => (
            <CriterionEvaluationCard key={item.criterion_id} evaluation={item} />
          ))}
        </div>
      </div>

      {/* Gaps, Recommendations, and Limitations */}
      <IdentifiedGaps gaps={review.identified_gaps} />
      <RevisionRecommendations recommendations={review.recommendations} />
      <EvidenceLimitations
        limitations={review.limitations}
        areasForHumanVerification={review.areas_for_human_verification}
      />
    </div>
  );
};

