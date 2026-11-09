import React from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  FileText,
  HelpCircle,
  XCircle,
} from 'lucide-react';
import { CriterionEvaluation, CriterionEvaluationStatus } from '../../types/submission';

interface CriterionEvaluationCardProps {
  evaluation: CriterionEvaluation;
}

export const CriterionEvaluationCard: React.FC<CriterionEvaluationCardProps> = ({
  evaluation,
}) => {
  const getStatusBadge = (status: CriterionEvaluationStatus) => {
    switch (status) {
      case 'met':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/40 bg-emerald-950/60 px-3 py-0.5 text-xs font-semibold text-emerald-400">
            <CheckCircle2 className="h-3.5 w-3.5" />
            Requirement Met
          </span>
        );
      case 'partially_met':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/40 bg-amber-950/60 px-3 py-0.5 text-xs font-semibold text-amber-300">
            <AlertTriangle className="h-3.5 w-3.5" />
            Partially Satisfied
          </span>
        );
      case 'not_demonstrated':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-rose-500/40 bg-rose-950/60 px-3 py-0.5 text-xs font-semibold text-rose-300">
            <XCircle className="h-3.5 w-3.5" />
            Not Demonstrated
          </span>
        );
      case 'unable_to_assess':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-slate-700 bg-slate-800/80 px-3 py-0.5 text-xs font-semibold text-slate-300">
            <HelpCircle className="h-3.5 w-3.5 text-slate-400" />
            Unable to Assess
          </span>
        );
    }
  };

  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-950/60 p-4 transition-all hover:border-slate-700">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-2.5">
          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-slate-900 border border-slate-800 font-mono text-xs font-bold text-slate-300 mt-0.5">
            #{evaluation.criterion_id}
          </span>
          <div>
            <h5 className="text-xs font-semibold text-white leading-snug">
              {evaluation.criterion_text}
            </h5>
          </div>
        </div>
        <div>{getStatusBadge(evaluation.status)}</div>
      </div>

      {/* Explanation */}
      <p className="mt-3 text-xs leading-relaxed text-slate-300 pl-8">
        {evaluation.explanation}
      </p>

      {/* Missing Information Alert if any */}
      {evaluation.missing_information && (
        <div className="mt-2.5 ml-8 rounded-lg border border-amber-500/20 bg-amber-950/20 p-2.5 text-xs text-amber-300/90 flex items-start gap-2">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-amber-400 mt-0.5" />
          <div>
            <strong className="font-semibold text-amber-200">Missing Information:</strong>{' '}
            {evaluation.missing_information}
          </div>
        </div>
      )}

      {/* Supporting Evidence Tags */}
      {evaluation.supporting_evidence_ids && evaluation.supporting_evidence_ids.length > 0 && (
        <div className="mt-3 ml-8 flex flex-wrap items-center gap-1.5 text-[11px] text-slate-400">
          <span className="text-slate-500">Supporting Evidence:</span>
          {evaluation.supporting_evidence_ids.map((id, idx) => (
            <span
              key={idx}
              className="inline-flex items-center gap-1 rounded bg-slate-900 px-2 py-0.5 text-slate-300 border border-slate-800 font-mono text-[10px]"
            >
              <FileText className="h-3 w-3 text-cyan-400" />
              {id}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

