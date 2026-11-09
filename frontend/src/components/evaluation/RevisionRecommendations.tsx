import React from 'react';
import { Lightbulb } from 'lucide-react';

interface RevisionRecommendationsProps {
  recommendations: string[];
}

export const RevisionRecommendations: React.FC<RevisionRecommendationsProps> = ({
  recommendations,
}) => {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div className="rounded-xl border border-indigo-500/30 bg-indigo-950/20 p-4">
      <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-indigo-300 mb-2.5">
        <Lightbulb className="h-4 w-4 text-indigo-400" />
        AI Revision Recommendations ({recommendations.length})
      </h4>
      <ul className="space-y-1.5">
        {recommendations.map((rec, idx) => (
          <li key={idx} className="flex items-start gap-2 text-xs text-indigo-200/90 leading-relaxed">
            <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-400" />
            <span>{rec}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

