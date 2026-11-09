import React from 'react';
import { AlertCircle, Clock, FileEdit, Lock } from 'lucide-react';
import { SubmissionStatus } from '../../types/submission';

interface SubmissionStatusBadgeProps {
  status: SubmissionStatus;
  className?: string;
}

export const SubmissionStatusBadge: React.FC<SubmissionStatusBadgeProps> = ({
  status,
  className = '',
}) => {
  switch (status) {
    case 'approved':
      return (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border border-emerald-500/40 bg-emerald-950/60 px-3 py-1 text-xs font-semibold text-emerald-400 shadow-sm shadow-emerald-950/50 ${className}`}
        >
          <Lock className="h-3.5 w-3.5" />
          Milestone Approved
        </span>
      );
    case 'submitted':
      return (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border border-cyan-500/40 bg-cyan-950/60 px-3 py-1 text-xs font-semibold text-cyan-300 ${className}`}
        >
          <Clock className="h-3.5 w-3.5" />
          Submitted for Client Review
        </span>
      );
    case 'revision_requested':
      return (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border border-rose-500/40 bg-rose-950/60 px-3 py-1 text-xs font-semibold text-rose-300 ${className}`}
        >
          <AlertCircle className="h-3.5 w-3.5" />
          Revision Requested
        </span>
      );
    case 'draft':
    default:
      return (
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border border-slate-700 bg-slate-800/80 px-3 py-1 text-xs font-semibold text-slate-300 ${className}`}
        >
          <FileEdit className="h-3.5 w-3.5 text-cyan-400" />
          Draft Submission
        </span>
      );
  }
};
