import React, { useState } from 'react';
import { Bot, Loader2, Sparkles, X } from 'lucide-react';

interface MilestoneGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (additionalInstructions?: string) => Promise<void>;
  projectTitle: string;
  projectBudget: number | string;
  currency: string;
}

export const MilestoneGeneratorModal: React.FC<MilestoneGeneratorModalProps> = ({
  isOpen,
  onClose,
  onGenerate,
  projectTitle,
  projectBudget,
  currency,
}) => {
  const [instructions, setInstructions] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    try {
      setIsGenerating(true);
      setError(null);
      await onGenerate(instructions.trim() || undefined);
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Generation failed. Check backend configuration.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md">
      <div className="relative w-full max-w-lg rounded-2xl border border-cyan-500/30 bg-slate-900 p-6 shadow-2xl shadow-cyan-950/40">
        {/* Close Button */}
        {!isGenerating && (
          <button
            onClick={onClose}
            className="absolute right-4 top-4 rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        )}

        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white shadow-lg shadow-cyan-500/30">
            <Bot className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              Generate Milestones with Gemini AI
              <Sparkles className="h-4 w-4 text-cyan-400" />
            </h3>
            <p className="text-xs text-slate-400">
              Transform unstructured project requirements into verifiable milestones
            </p>
          </div>
        </div>

        {/* Project Target Bar */}
        <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950/60 p-3.5 text-xs text-slate-300 flex items-center justify-between">
          <div className="truncate pr-2">
            <span className="text-slate-500">Project:</span> <strong className="text-white">{projectTitle}</strong>
          </div>
          <div className="shrink-0 font-mono font-bold text-cyan-400">
            {Number(projectBudget).toLocaleString('en-US', { minimumFractionDigits: 2 })} {currency}
          </div>
        </div>

        {/* Optional guidance input */}
        <div className="mt-4">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
            Guidance & Specific Instructions (Optional)
          </label>
          <textarea
            rows={3}
            disabled={isGenerating}
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            placeholder="e.g., Prioritize database architecture in Milestone 1, allocate 25% budget to QA testing, keep durations under 10 days each..."
            className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-xs text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none disabled:opacity-50"
          />
          <p className="mt-1 text-[11px] text-slate-500">
            Gemini guarantees sequential deliverables, objective acceptance criteria, and exact 100% budget balancing.
          </p>
        </div>

        {/* Error message */}
        {error && (
          <div className="mt-3 rounded-lg border border-rose-500/30 bg-rose-950/40 p-3 text-xs text-rose-300">
            {error}
          </div>
        )}

        {/* Loading State Banner */}
        {isGenerating && (
          <div className="mt-4 rounded-xl border border-cyan-500/20 bg-cyan-950/20 p-4 text-center">
            <Loader2 className="mx-auto h-7 w-7 animate-spin text-cyan-400" />
            <h4 className="mt-2 text-xs font-semibold text-cyan-300">
              Gemini AI is analyzing project requirements...
            </h4>
            <p className="mt-1 text-[11px] text-slate-400">
              Calculating objective criteria & cent-exact budget allocations
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="mt-6 flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
          <button
            type="button"
            disabled={isGenerating}
            onClick={onClose}
            className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={isGenerating}
            onClick={handleGenerate}
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 px-5 py-2 text-xs font-semibold text-white shadow-lg shadow-cyan-950/50 hover:from-cyan-400 hover:to-indigo-500 disabled:opacity-50 transition-all"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Generating Plan...
              </>
            ) : (
              <>
                <Sparkles className="h-3.5 w-3.5" />
                Generate Milestones
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

