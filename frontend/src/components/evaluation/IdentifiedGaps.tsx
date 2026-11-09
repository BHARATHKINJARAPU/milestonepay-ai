import React from 'react';
import { AlertCircle } from 'lucide-react';

interface IdentifiedGapsProps {
  gaps: string[];
}

export const IdentifiedGaps: React.FC<IdentifiedGapsProps> = ({ gaps }) => {
  if (!gaps || gaps.length === 0) return null;

  return (
    <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-4">
      <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-rose-300 mb-2.5">
        <AlertCircle className="h-4 w-4 text-rose-400" />
        Identified Deliverable Gaps ({gaps.length})
      </h4>
      <ul className="space-y-1.5">
        {gaps.map((gap, idx) => (
          <li key={idx} className="flex items-start gap-2 text-xs text-rose-200/90 leading-relaxed">
            <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-rose-400" />
            <span>{gap}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

