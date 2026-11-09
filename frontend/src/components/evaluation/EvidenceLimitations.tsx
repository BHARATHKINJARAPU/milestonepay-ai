import React from 'react';
import { ShieldAlert, UserCheck } from 'lucide-react';

interface EvidenceLimitationsProps {
  limitations: string[];
  areasForHumanVerification: string[];
}

export const EvidenceLimitations: React.FC<EvidenceLimitationsProps> = ({
  limitations,
  areasForHumanVerification,
}) => {
  const hasContent = limitations.length > 0 || areasForHumanVerification.length > 0;
  if (!hasContent) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Evidence Limitations */}
      {limitations.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
          <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
            <ShieldAlert className="h-4 w-4 text-amber-400" />
            Evidence Limitations ({limitations.length})
          </h4>
          <ul className="space-y-1.5">
            {limitations.map((lim, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-slate-400 leading-relaxed">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                <span>{lim}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Human Verification Required */}
      {areasForHumanVerification.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
          <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
            <UserCheck className="h-4 w-4 text-cyan-400" />
            Manual Client Verification Required ({areasForHumanVerification.length})
          </h4>
          <ul className="space-y-1.5">
            {areasForHumanVerification.map((area, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-slate-400 leading-relaxed">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-400" />
                <span>{area}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

