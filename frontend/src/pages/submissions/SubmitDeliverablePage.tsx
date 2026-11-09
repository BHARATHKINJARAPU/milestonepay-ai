import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link, useOutletContext } from 'react-router-dom';
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  FileCheck,
  Globe,
  Loader2,
  Send,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { DashboardHeader } from '../../components/dashboard/DashboardHeader';
import { EvidenceUploader } from '../../components/submissions/EvidenceUploader';
import { EvidenceFileList } from '../../components/submissions/EvidenceFileList';
import {
  createSubmission,
  deleteSubmissionEvidence,
  getMilestonePlans,
  getMilestoneSubmissions,
  getProject,
  submitDeliverable,
  uploadSubmissionEvidence,
} from '../../lib/api';
import { Milestone } from '../../types/milestone';
import { Project } from '../../types/project';
import { MilestoneSubmission } from '../../types/submission';

interface OutletContextType {
  onOpenMobileMenu: () => void;
}

export const SubmitDeliverablePage: React.FC = () => {
  const { projectId, milestoneId } = useParams<{ projectId: string; milestoneId: string }>();
  const navigate = useNavigate();
  const { onOpenMobileMenu } = useOutletContext<OutletContextType>();

  const [project, setProject] = useState<Project | null>(null);
  const [milestone, setMilestone] = useState<Milestone | null>(null);
  const [activeDraft, setActiveDraft] = useState<MilestoneSubmission | null>(null);

  // Form states
  const [description, setDescription] = useState('');
  const [notes, setNotes] = useState('');
  const [demoUrl, setDemoUrl] = useState('');

  const [isLoading, setIsLoading] = useState(true);
  const [isSubmittingWork, setIsSubmittingWork] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadData = async () => {
    if (!projectId || !milestoneId) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const proj = await getProject(projectId);
      setProject(proj);

      // Fetch milestone plans to find the agreed milestone
      const allPlans = await getMilestonePlans(projectId);
      const agreedPlan = allPlans.plans.find((p) => p.status === 'agreed') || allPlans.plans[0];

      if (agreedPlan) {
        const foundMilestone = agreedPlan.milestones.find((m) => m.id === milestoneId);
        if (foundMilestone) {
          setMilestone(foundMilestone);
        }
      }

      // Check for existing submissions to see if there is an active draft
      const subs = await getMilestoneSubmissions(projectId, milestoneId);
      const draft = subs.submissions.find((s) => s.status === 'draft');
      if (draft) {
        setActiveDraft(draft);
        setDescription(draft.description);
        setNotes(draft.notes || '');
        setDemoUrl(draft.demonstration_url || '');
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to initialize submission page.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId, milestoneId]);

  // Step 1: Create draft if not exists
  const handleSaveDraft = async () => {
    if (!projectId || !milestoneId) return null;
    if (!description.trim() || description.length < 10) {
      setErrorMessage('Please provide a completion description (minimum 10 characters).');
      return null;
    }

    try {
      setErrorMessage(null);
      if (!activeDraft) {
        const created = await createSubmission(projectId, milestoneId, {
          description: description.trim(),
          notes: notes.trim() || undefined,
          demonstration_url: demoUrl.trim() || undefined,
        });
        setActiveDraft(created);
        return created;
      }
      return activeDraft;
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to save draft.');
      return null;
    }
  };

  // Upload evidence
  const handleUploadEvidence = async (files: File[]) => {
    let draft = activeDraft;
    if (!draft) {
      draft = await handleSaveDraft();
      if (!draft) return;
    }
    const updated = await uploadSubmissionEvidence(draft.id, files);
    setActiveDraft(updated);
  };

  // Delete evidence
  const handleDeleteEvidence = async (evidenceId: string) => {
    if (!activeDraft) return;
    const updated = await deleteSubmissionEvidence(activeDraft.id, evidenceId);
    setActiveDraft(updated);
  };

  // Final Submit
  const handleFinalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim() || description.length < 10) {
      setErrorMessage('Please describe the deliverable work completed (minimum 10 characters).');
      return;
    }

    try {
      setIsSubmittingWork(true);
      setErrorMessage(null);

      let draft = activeDraft;
      if (!draft) {
        draft = await createSubmission(projectId!, milestoneId!, {
          description: description.trim(),
          notes: notes.trim() || undefined,
          demonstration_url: demoUrl.trim() || undefined,
        });
        setActiveDraft(draft);
      }

      // Finalize submission & trigger Gemini AI evaluation
      const submitted = await submitDeliverable(draft.id);
      // Navigate to submission detail page to view evaluation
      navigate(`/projects/${projectId}/milestones/${milestoneId}/submissions/${submitted.id}`);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to submit deliverable.');
    } finally {
      setIsSubmittingWork(false);
    }
  };

  if (isLoading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center text-slate-400 space-y-3 font-mono text-xs">
        <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
        <span>Loading milestone deliverable form...</span>
      </div>
    );
  }

  if (errorMessage && !project) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-900/60 text-xs text-rose-300 flex items-center justify-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
        <Link
          to={`/projects/${projectId}/milestones`}
          className="inline-flex items-center gap-2 text-xs font-semibold text-cyan-400 hover:text-cyan-300"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Milestones</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <DashboardHeader
        title="Submit Milestone Deliverables"
        subtitle={milestone ? `Milestone #${milestone.sequence_number}: ${milestone.title}` : 'Deliverable Submission'}
        onOpenMobileMenu={onOpenMobileMenu}
      />

      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-3 text-xs">
        <Link
          to={`/projects/${projectId}/milestones`}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900/80 px-3 py-1.5 font-semibold text-slate-300 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Milestone Workspace
        </Link>
        <span className="text-slate-600">/</span>
        <span className="text-slate-400">
          Attempt #{activeDraft?.attempt_number || 1} (Draft)
        </span>
      </div>

      {errorMessage && (
        <div className="rounded-xl border border-rose-500/30 bg-rose-950/40 p-4 text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-400" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* 2-Column Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Submission Form & Evidence Uploader */}
        <div className="lg:col-span-7 space-y-6">
          <form onSubmit={handleFinalSubmit} className="space-y-6">
            {/* Completion Description */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider font-mono">
                1. Work Completion Description
              </h3>
              <p className="text-xs text-slate-400">
                Explain how you completed this milestone's requirements and which deliverables were produced.
              </p>
              <textarea
                rows={5}
                required
                disabled={isSubmittingWork}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g., Implemented all database schemas with foreign keys, wrote pytest automated suite with 100% pass rate, and deployed Docker container..."
                className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3.5 text-xs text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
              />
            </div>

            {/* Implementation Notes & Demo URL */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider font-mono">
                2. Technical Notes & Live Demonstration
              </h3>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Implementation Notes (Optional)
                </label>
                <textarea
                  rows={3}
                  disabled={isSubmittingWork}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g., Architecture trade-offs, configuration settings, or local setup instructions..."
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-xs text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                  <Globe className="h-3.5 w-3.5 text-cyan-400" />
                  Demonstration URL (Optional)
                </label>
                <input
                  type="url"
                  disabled={isSubmittingWork}
                  value={demoUrl}
                  onChange={(e) => setDemoUrl(e.target.value)}
                  placeholder="https://staging.example.com or Figma preview link"
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-xs text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
                />
                <span className="mt-1 block text-[11px] text-slate-500">
                  Displayed for manual client inspection. URLs are never crawled automatically.
                </span>
              </div>
            </div>

            {/* Evidence File Uploader Section */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider font-mono">
                3. Verification Evidence Artifacts
              </h3>
              <p className="text-xs text-slate-400">
                Attach screenshots, PDF reports, or text logs proving completion of acceptance criteria.
              </p>

              <EvidenceUploader
                currentCount={activeDraft?.evidence.length || 0}
                onUpload={handleUploadEvidence}
                disabled={isSubmittingWork}
              />

              {activeDraft && activeDraft.evidence.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-800">
                  <h4 className="text-xs font-semibold uppercase text-slate-400 mb-2">
                    Attached Evidence ({activeDraft.evidence.length})
                  </h4>
                  <EvidenceFileList
                    submissionId={activeDraft.id}
                    evidence={activeDraft.evidence}
                    canDelete={true}
                    onDelete={handleDeleteEvidence}
                  />
                </div>
              )}
            </div>

            {/* Submit Action Bar */}
            <div className="rounded-2xl border border-cyan-500/20 bg-gradient-to-r from-slate-900/90 to-cyan-950/40 p-6 backdrop-blur-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="text-xs text-slate-400">
                <span className="flex items-center gap-1 text-cyan-400 font-semibold mb-0.5">
                  <Sparkles className="h-3.5 w-3.5" />
                  Automated Gemini AI Audit
                </span>
                <span>Submitting locks evidence and triggers AI verification against agreed criteria.</span>
              </div>

              <button
                type="submit"
                disabled={isSubmittingWork}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 px-6 py-3 text-xs font-semibold text-white shadow-xl shadow-cyan-950/60 hover:from-cyan-400 hover:to-indigo-500 transition-all disabled:opacity-50 shrink-0"
              >
                {isSubmittingWork ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Submitting & Running AI Audit...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Submit Work for Client Review
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Right Column: Source of Truth (Agreed Milestone Criteria) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2 text-white text-sm font-semibold">
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
                <span>Agreed Acceptance Criteria</span>
              </div>
              <span className="text-[10px] font-mono uppercase bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">
                Source of Truth
              </span>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Gemini AI will evaluate your submission exclusively against these criteria:
            </p>

            <ul className="space-y-3">
              {(milestone?.acceptance_criteria || []).map((crit, idx) => (
                <li
                  key={idx}
                  className="rounded-xl border border-slate-800 bg-slate-950/70 p-3.5 text-xs text-slate-300 space-y-1"
                >
                  <div className="font-mono text-[11px] font-bold text-cyan-400">
                    Criterion #{idx + 1}
                  </div>
                  <div className="leading-relaxed">{crit}</div>
                </li>
              ))}
            </ul>
          </div>

          {/* Agreed Deliverables Checklist */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <FileCheck className="h-4 w-4 text-indigo-400" />
              Required Deliverables
            </h4>
            <ul className="space-y-2">
              {(milestone?.deliverables || []).map((deliv, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                  <CheckCircle2 className="h-3.5 w-3.5 text-cyan-400 mt-0.5 shrink-0" />
                  <span>{deliv}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
