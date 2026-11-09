import React, { useState } from 'react';
import { Plus, Trash2, X } from 'lucide-react';
import { Milestone, MilestoneInput } from '../../types/milestone';

interface MilestoneEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  milestone: Milestone;
  onSave: (updated: MilestoneInput) => Promise<void>;
}

export const MilestoneEditorModal: React.FC<MilestoneEditorModalProps> = ({
  isOpen,
  onClose,
  milestone,
  onSave,
}) => {
  const [title, setTitle] = useState(milestone.title);
  const [description, setDescription] = useState(milestone.description);
  const [duration, setDuration] = useState(milestone.estimated_duration_days);
  const [budgetPercentage, setBudgetPercentage] = useState(Number(milestone.budget_percentage));
  const [deliverables, setDeliverables] = useState<string[]>([...milestone.deliverables]);
  const [criteria, setCriteria] = useState<string[]>([...milestone.acceptance_criteria]);
  const [newDeliverable, setNewDeliverable] = useState('');
  const [newCriterion, setNewCriterion] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAddDeliverable = () => {
    if (!newDeliverable.trim()) return;
    setDeliverables([...deliverables, newDeliverable.trim()]);
    setNewDeliverable('');
  };

  const handleRemoveDeliverable = (idx: number) => {
    if (deliverables.length <= 1) return;
    setDeliverables(deliverables.filter((_, i) => i !== idx));
  };

  const handleAddCriterion = () => {
    if (!newCriterion.trim()) return;
    setCriteria([...criteria, newCriterion.trim()]);
    setNewCriterion('');
  };

  const handleRemoveCriterion = (idx: number) => {
    if (criteria.length <= 1) return;
    setCriteria(criteria.filter((_, i) => i !== idx));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      setError('Title and description are required.');
      return;
    }
    if (deliverables.length === 0 || criteria.length === 0) {
      setError('At least one deliverable and acceptance criterion are required.');
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      await onSave({
        id: milestone.id,
        sequence_number: milestone.sequence_number,
        title: title.trim(),
        description: description.trim(),
        estimated_duration_days: Number(duration),
        budget_percentage: Number(budgetPercentage),
        deliverables,
        acceptance_criteria: criteria,
        dependencies: milestone.dependencies,
      });
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update milestone.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md">
      <div className="relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
        >
          <X className="h-5 w-5" />
        </button>

        <h3 className="text-lg font-bold text-white tracking-tight">
          Edit Milestone #{milestone.sequence_number}
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Modify scope, criteria, or allocation before bilateral plan submission.
        </p>

        {error && (
          <div className="mt-3 rounded-lg border border-rose-500/30 bg-rose-950/40 p-3 text-xs text-rose-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSave} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-300 mb-1">
              Milestone Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-xs text-white focus:border-cyan-500 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase text-slate-300 mb-1">
              Description
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-xs text-white focus:border-cyan-500 focus:outline-none"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase text-slate-300 mb-1">
                Duration (Days)
              </label>
              <input
                type="number"
                min={1}
                max={365}
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-xs text-white focus:border-cyan-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase text-slate-300 mb-1">
                Budget Percentage (%)
              </label>
              <input
                type="number"
                step="0.1"
                min={1}
                max={100}
                value={budgetPercentage}
                onChange={(e) => setBudgetPercentage(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-xs text-white focus:border-cyan-500 focus:outline-none"
                required
              />
            </div>
          </div>

          {/* Deliverables List */}
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-300 mb-1.5">
              Deliverables
            </label>
            <div className="space-y-1.5 mb-2">
              {deliverables.map((item, idx) => (
                <div key={idx} className="flex items-center gap-2 rounded bg-slate-950 p-2 text-xs border border-slate-800">
                  <span className="flex-1 text-slate-300">{item}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveDeliverable(idx)}
                    className="text-slate-500 hover:text-rose-400"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newDeliverable}
                onChange={(e) => setNewDeliverable(e.target.value)}
                placeholder="Add deliverable..."
                className="flex-1 rounded-lg border border-slate-700 bg-slate-950 p-2 text-xs text-white"
              />
              <button
                type="button"
                onClick={handleAddDeliverable}
                className="inline-flex items-center gap-1 rounded-lg bg-slate-800 px-3 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-700"
              >
                <Plus className="h-3.5 w-3.5" /> Add
              </button>
            </div>
          </div>

          {/* Acceptance Criteria List */}
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-300 mb-1.5">
              Acceptance Criteria
            </label>
            <div className="space-y-1.5 mb-2">
              {criteria.map((item, idx) => (
                <div key={idx} className="flex items-center gap-2 rounded bg-slate-950 p-2 text-xs border border-slate-800">
                  <span className="flex-1 text-slate-300">{item}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveCriterion(idx)}
                    className="text-slate-500 hover:text-rose-400"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={newCriterion}
                onChange={(e) => setNewCriterion(e.target.value)}
                placeholder="Add acceptance criterion..."
                className="flex-1 rounded-lg border border-slate-700 bg-slate-950 p-2 text-xs text-white"
              />
              <button
                type="button"
                onClick={handleAddCriterion}
                className="inline-flex items-center gap-1 rounded-lg bg-slate-800 px-3 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-700"
              >
                <Plus className="h-3.5 w-3.5" /> Add
              </button>
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="rounded-lg bg-cyan-600 px-5 py-2 text-xs font-semibold text-white hover:bg-cyan-500 disabled:opacity-50"
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

