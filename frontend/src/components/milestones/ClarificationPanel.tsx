import React from 'react';
import { AlertTriangle, CheckSquare, HelpCircle, Info, ShieldAlert } from 'lucide-react';

interface ClarificationPanelProps {
  needsClarification: boolean;
  assumptions: string[];
  clarifyingQuestions: string[];
  risks: string[];
}

export const ClarificationPanel: React.FC<ClarificationPanelProps> = ({
  needsClarification,
  assumptions,
  clarifyingQuestions,
  risks,
}) => {
  const hasContent =
    assumptions.length > 0 || clarifyingQuestions.length > 0 || risks.length > 0;

  if (!hasContent && !needsClarification) {
    return null;
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
      {/* Alert Banner if Major Clarifications Needed */}
      {needsClarification && (
        <div className="mb-5 flex items-start gap-3 rounded-lg border border-amber-500/30 bg-amber-950/30 p-4 text-amber-300">
          <AlertTriangle className="h-5 w-5 shrink-0 text-amber-400 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-amber-200">
              Requirements Ambiguity Detected by Gemini AI
            </h4>
            <p className="mt-1 text-xs text-amber-300/80 leading-relaxed">
              The project brief contained open-ended requirements. Review the clarifying questions and baseline assumptions below before formal bilateral agreement.
            </p>
          </div>
        </div>
      )}

      <div className="flex items-center gap-2 mb-4">
        <Info className="h-4 w-4 text-cyan-400" />
        <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
          AI Analysis: Assumptions & Risk Intelligence
        </h3>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {/* Assumptions */}
        {assumptions.length > 0 && (
          <div className="rounded-lg bg-slate-950/60 p-4 border border-slate-800/80">
            <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase text-slate-300 mb-2">
              <CheckSquare className="h-3.5 w-3.5 text-indigo-400" />
              Baseline Assumptions ({assumptions.length})
            </h4>
            <ul className="space-y-2">
              {assumptions.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-400" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Clarifying Questions */}
        {clarifyingQuestions.length > 0 && (
          <div className="rounded-lg bg-slate-950/60 p-4 border border-slate-800/80">
            <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase text-slate-300 mb-2">
              <HelpCircle className="h-3.5 w-3.5 text-amber-400" />
              Clarifying Questions ({clarifyingQuestions.length})
            </h4>
            <ul className="space-y-2">
              {clarifyingQuestions.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Risks */}
        {risks.length > 0 && (
          <div className="rounded-lg bg-slate-950/60 p-4 border border-slate-800/80">
            <h4 className="flex items-center gap-1.5 text-xs font-semibold uppercase text-slate-300 mb-2">
              <ShieldAlert className="h-3.5 w-3.5 text-rose-400" />
              Potential Scope Risks ({risks.length})
            </h4>
            <ul className="space-y-2">
              {risks.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-rose-400" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

