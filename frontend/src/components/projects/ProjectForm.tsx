import React, { useState } from 'react';
import { DollarSign, Calendar, Type, Loader2 } from 'lucide-react';
import { ProjectCreateInput, ProjectUpdateInput } from '../../types/project';

interface ProjectFormProps {
  initialValues?: {
    title: string;
    description: string;
    budget_amount: number | string;
    currency: string;
    deadline?: string | null;
  };
  onSubmit: (values: ProjectCreateInput | ProjectUpdateInput) => Promise<void>;
  submitLabel?: string;
  isSubmitting?: boolean;
}

export const ProjectForm: React.FC<ProjectFormProps> = ({
  initialValues,
  onSubmit,
  submitLabel = 'Save Project',
  isSubmitting = false,
}) => {
  const [title, setTitle] = useState(initialValues?.title || '');
  const [description, setDescription] = useState(initialValues?.description || '');
  const [budgetAmount, setBudgetAmount] = useState(initialValues?.budget_amount?.toString() || '');
  const [currency, setCurrency] = useState(initialValues?.currency || 'USD');
  const [deadline, setDeadline] = useState(initialValues?.deadline || '');
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (title.trim().length < 3) {
      setValidationError('Project title must be at least 3 characters.');
      return;
    }

    if (description.trim().length < 10) {
      setValidationError('Project description must be at least 10 characters.');
      return;
    }

    const numericBudget = parseFloat(budgetAmount);
    if (isNaN(numericBudget) || numericBudget <= 0) {
      setValidationError('Budget must be a positive number greater than 0.');
      return;
    }

    await onSubmit({
      title: title.trim(),
      description: description.trim(),
      budget_amount: numericBudget,
      currency,
      deadline: deadline ? deadline : null,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {validationError && (
        <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-900/60 text-xs text-rose-300">
          {validationError}
        </div>
      )}

      {/* Title */}
      <div className="space-y-1.5">
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
          Project Title <span className="text-rose-400">*</span>
        </label>
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-500">
            <Type className="h-4 w-4" />
          </div>
          <input
            type="text"
            required
            placeholder="e.g. Mobile App Frontend Redesign"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="block w-full rounded-xl bg-slate-900/90 border border-slate-800 pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Description */}
      <div className="space-y-1.5">
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
          Project Description & Scope <span className="text-rose-400">*</span>
        </label>
        <div className="relative">
          <textarea
            required
            rows={4}
            placeholder="Describe the project objectives, deliverables, and expectations. You can paste rough unstructured briefs here."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="block w-full rounded-xl bg-slate-900/90 border border-slate-800 p-3.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <p className="text-[11px] text-slate-500">
          Tip: In future phases, AI will parse this description directly into verifiable milestones and acceptance criteria.
        </p>
      </div>

      {/* Budget and Currency */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="sm:col-span-2 space-y-1.5">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
            Total Budget Amount <span className="text-rose-400">*</span>
          </label>
          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-500">
              <DollarSign className="h-4 w-4" />
            </div>
            <input
              type="number"
              step="0.01"
              min="1"
              required
              placeholder="e.g. 2500.00"
              value={budgetAmount}
              onChange={(e) => setBudgetAmount(e.target.value)}
              className="block w-full rounded-xl bg-slate-900/90 border border-slate-800 pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
            Currency
          </label>
          <select
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            className="block w-full rounded-xl bg-slate-900/90 border border-slate-800 px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          >
            <option value="USD">USD ($)</option>
            <option value="EUR">EUR (€)</option>
            <option value="GBP">GBP (£)</option>
            <option value="CAD">CAD ($)</option>
            <option value="AUD">AUD ($)</option>
          </select>
        </div>
      </div>

      {/* Deadline */}
      <div className="space-y-1.5">
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
          Target Deadline (Optional)
        </label>
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-500">
            <Calendar className="h-4 w-4" />
          </div>
          <input
            type="date"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            className="block w-full rounded-xl bg-slate-900/90 border border-slate-800 pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 [color-scheme:dark]"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full py-3 px-4 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 shadow-lg shadow-blue-600/25 transition-all text-sm flex items-center justify-center gap-2 disabled:opacity-50"
      >
        {isSubmitting ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Processing...</span>
          </>
        ) : (
          <span>{submitLabel}</span>
        )}
      </button>
    </form>
  );
};
