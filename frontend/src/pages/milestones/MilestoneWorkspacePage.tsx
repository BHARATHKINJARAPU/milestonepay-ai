import React, { useEffect, useState } from 'react';
import { useParams, Link, useOutletContext } from 'react-router-dom';
import {
  AlertCircle,
  ArrowLeft,
  Bot,
  Calendar,
  CalendarDays,
  DollarSign,
  FileText,
  History,
  LayoutGrid,
  Loader2,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { DashboardHeader } from '../../components/dashboard/DashboardHeader';
import { MilestoneCard } from '../../components/milestones/MilestoneCard';
import { MilestoneBudgetSummary } from '../../components/milestones/MilestoneBudgetSummary';
import { ClarificationPanel } from '../../components/milestones/ClarificationPanel';
import { PlanApprovalPanel } from '../../components/milestones/PlanApprovalPanel';
import { MilestoneTimeline } from '../../components/milestones/MilestoneTimeline';
import { MilestoneGeneratorModal } from '../../components/milestones/MilestoneGeneratorModal';
import { MilestoneEditorModal } from '../../components/milestones/MilestoneEditorModal';
import { useAuth } from '../../context/AuthContext';
import {
  approveMilestonePlan,
  generateMilestonePlan,
  getMilestonePlans,
  getProject,
  requestMilestonePlanRevision,
  submitMilestonePlanForApproval,
  updateMilestonePlan,
} from '../../lib/api';
import { Milestone, MilestoneInput, MilestonePlan } from '../../types/milestone';
import { Project } from '../../types/project';

interface OutletContextType {
  onOpenMobileMenu: () => void;
}

export const MilestoneWorkspacePage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { user } = useAuth();
  const { onOpenMobileMenu } = useOutletContext<OutletContextType>();

  const [project, setProject] = useState<Project | null>(null);
  const [plans, setPlans] = useState<MilestonePlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<MilestonePlan | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'cards' | 'timeline'>('cards');

  // Modals
  const [isGeneratorOpen, setIsGeneratorOpen] = useState(false);
  const [editingMilestone, setEditingMilestone] = useState<Milestone | null>(null);

  const loadData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [projData, plansData] = await Promise.all([
        getProject(projectId),
        getMilestonePlans(projectId),
      ]);
      setProject(projData);
      setPlans(plansData.plans);
      if (plansData.plans.length > 0) {
        setSelectedPlan(plansData.plans[0]);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to load milestone workspace.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  // Handle AI generation
  const handleGeneratePlan = async (additionalInstructions?: string) => {
    if (!projectId) return;
    const newPlan = await generateMilestonePlan(projectId, {
      additional_instructions: additionalInstructions,
    });
    setPlans((prev) => [newPlan, ...prev]);
    setSelectedPlan(newPlan);
  };

  // Handle Submission for bilateral approval
  const handleSubmitForApproval = async () => {
    if (!projectId || !selectedPlan) return;
    const updated = await submitMilestonePlanForApproval(projectId, selectedPlan.id);
    setSelectedPlan(updated);
    setPlans((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
  };

  // Handle user approval
  const handleApprovePlan = async () => {
    if (!projectId || !selectedPlan) return;
    const updated = await approveMilestonePlan(projectId, selectedPlan.id);
    setSelectedPlan(updated);
    setPlans((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
    // Also refresh project state since project status might have transitioned to active
    const refreshedProj = await getProject(projectId);
    setProject(refreshedProj);
  };

  // Handle revision request
  const handleRequestRevision = async (comment: string) => {
    if (!projectId || !selectedPlan) return;
    const updated = await requestMilestonePlanRevision(projectId, selectedPlan.id, comment);
    setSelectedPlan(updated);
    setPlans((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
  };

  // Handle milestone edit save
  const handleSaveMilestoneEdit = async (updatedMilestone: MilestoneInput) => {
    if (!projectId || !selectedPlan) return;
    const updatedMilestones: MilestoneInput[] = selectedPlan.milestones.map((m) => {
      if (m.sequence_number === updatedMilestone.sequence_number) {
        return updatedMilestone;
      }
      return {
        id: m.id,
        sequence_number: m.sequence_number,
        title: m.title,
        description: m.description,
        deliverables: m.deliverables,
        acceptance_criteria: m.acceptance_criteria,
        estimated_duration_days: m.estimated_duration_days,
        budget_percentage: Number(m.budget_percentage),
        dependencies: m.dependencies,
      };
    });

    const updated = await updateMilestonePlan(projectId, selectedPlan.id, {
      milestones: updatedMilestones,
    });
    setSelectedPlan(updated);
    setPlans((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
  };

  if (isLoading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center text-slate-400 space-y-3 font-mono text-xs">
        <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
        <span>Loading milestone workspace...</span>
      </div>
    );
  }

  if (errorMessage || !project) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-900/60 text-xs text-rose-300 flex items-center justify-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{errorMessage || 'Project could not be found.'}</span>
        </div>
        <Link
          to="/projects"
          className="inline-flex items-center gap-2 text-xs font-semibold text-cyan-400 hover:text-cyan-300"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Projects</span>
        </Link>
      </div>
    );
  }

  const isPlanEditable =
    selectedPlan?.status === 'draft' || selectedPlan?.status === 'revision_requested';
  const isFreelancer = project?.members.some((m) => m.user_id === user?.id && m.role === 'freelancer');
  const isClient = project?.members.some((m) => m.user_id === user?.id && m.role === 'client');

  return (
    <div className="space-y-8 pb-16">
      {/* Top Header */}
      <DashboardHeader
        title="Milestone Agreement Workspace"
        subtitle={`Project: ${project.title}`}
        onOpenMobileMenu={onOpenMobileMenu}
      />

      {/* Project Meta Bar */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 backdrop-blur-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link
            to={`/projects/${project.id}`}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white hover:border-slate-700 transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Project Details
          </Link>
          <div className="h-4 w-px bg-slate-800" />
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span className="flex items-center gap-1 font-mono font-bold text-white">
              <DollarSign className="h-3.5 w-3.5 text-cyan-400" />
              {Number(project.budget_amount).toLocaleString('en-US', { minimumFractionDigits: 2 })} {project.currency}
            </span>
            {project.deadline && (
              <span className="flex items-center gap-1">
                <Calendar className="h-3.5 w-3.5 text-slate-500" />
                Target: {new Date(project.deadline).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>

        {/* Plan Version Selector */}
        {plans.length > 0 && (
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-slate-400" />
            <span className="text-xs text-slate-400">Plan Version:</span>
            <select
              value={selectedPlan?.id || ''}
              onChange={(e) => {
                const found = plans.find((p) => p.id === e.target.value);
                if (found) setSelectedPlan(found);
              }}
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs font-semibold text-slate-200 focus:border-cyan-500 focus:outline-none"
            >
              {plans.map((p) => (
                <option key={p.id} value={p.id}>
                  v{p.version} — {p.status.toUpperCase()} ({p.generation_source.toUpperCase()})
                </option>
              ))}
            </select>
            <button
              onClick={() => setIsGeneratorOpen(true)}
              className="inline-flex items-center gap-1.5 rounded-lg bg-cyan-600/20 border border-cyan-500/30 px-3 py-1.5 text-xs font-semibold text-cyan-300 hover:bg-cyan-600/30 transition-colors"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              New AI Version
            </button>
          </div>
        )}
      </div>

      {/* No Plans Empty State */}
      {plans.length === 0 && (
        <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/30 p-12 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-cyan-500/20 to-indigo-500/20 border border-cyan-500/30 text-cyan-400">
            <Sparkles className="h-8 w-8" />
          </div>
          <h3 className="mt-4 text-lg font-bold text-white tracking-tight">
            No Milestone Plan Proposed Yet
          </h3>
          <p className="mx-auto mt-2 max-w-md text-xs text-slate-400 leading-relaxed">
            Let Gemini AI decompose your project brief into measurable milestones, concrete deliverables, acceptance criteria, and exact 100% budget allocations.
          </p>
          <div className="mt-6 flex justify-center">
            <button
              onClick={() => setIsGeneratorOpen(true)}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 px-6 py-3 text-xs font-semibold text-white shadow-xl shadow-cyan-950 hover:from-cyan-400 hover:to-indigo-500 transition-all"
            >
              <Bot className="h-4 w-4" />
              Generate Milestone Plan with Gemini AI
            </button>
          </div>
        </div>
      )}

      {/* Main Workspace (When Plan Exists) */}
      {selectedPlan && (
        <div className="space-y-8">
          {/* Executive Summary Card */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
                <FileText className="h-4 w-4" />
                Project Scope Summary
              </div>
              <span className="text-[11px] font-mono text-slate-500">
                Source: {selectedPlan.generation_source === 'ai' ? `Google Gemini (${selectedPlan.ai_model || '2.5 Flash'})` : 'Manual Authoring'}
              </span>
            </div>
            <p className="mt-3 text-sm leading-relaxed text-slate-200">
              {selectedPlan.project_summary}
            </p>
          </div>

          {/* Two-Party Approval Panel */}
          <PlanApprovalPanel
            plan={selectedPlan}
            members={project.members}
            currentUser={user}
            onSubmitForApproval={handleSubmitForApproval}
            onApprove={handleApprovePlan}
            onRequestRevision={handleRequestRevision}
          />

          {/* AI Intelligence / Clarifications Panel */}
          <ClarificationPanel
            needsClarification={selectedPlan.needs_clarification}
            assumptions={selectedPlan.assumptions}
            clarifyingQuestions={selectedPlan.clarifying_questions}
            risks={selectedPlan.risks}
          />

          {/* Budget Allocation Summary */}
          <MilestoneBudgetSummary
            totalBudget={selectedPlan.total_amount}
            currency={selectedPlan.currency}
            milestones={selectedPlan.milestones}
          />

          {/* View Mode Tabs */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setActiveTab('cards')}
                className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition-all ${
                  activeTab === 'cards'
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <LayoutGrid className="h-4 w-4" />
                Milestone Cards ({selectedPlan.milestones.length})
              </button>
              <button
                onClick={() => setActiveTab('timeline')}
                className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition-all ${
                  activeTab === 'timeline'
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <CalendarDays className="h-4 w-4" />
                Roadmap Timeline
              </button>
            </div>

            {isPlanEditable && (
              <span className="text-[11px] text-slate-500">
                Plan is editable. Click "Edit" on any milestone to adjust details.
              </span>
            )}
          </div>

          {/* Active Tab View */}
          {activeTab === 'cards' ? (
            <div className="space-y-5">
              {selectedPlan.milestones
                .sort((a, b) => a.sequence_number - b.sequence_number)
                .map((m) => (
                  <MilestoneCard
                    key={m.id}
                    milestone={m}
                    currency={selectedPlan.currency}
                    projectId={projectId}
                    planStatus={selectedPlan.status}
                    isFreelancer={isFreelancer}
                    isClient={isClient}
                    isEditable={isPlanEditable}
                    onEdit={(milestone) => setEditingMilestone(milestone)}
                  />
                ))}
            </div>
          ) : (
            <MilestoneTimeline
              milestones={selectedPlan.milestones}
              currency={selectedPlan.currency}
            />
          )}
        </div>
      )}

      {/* AI Generator Modal */}
      <MilestoneGeneratorModal
        isOpen={isGeneratorOpen}
        onClose={() => setIsGeneratorOpen(false)}
        onGenerate={handleGeneratePlan}
        projectTitle={project.title}
        projectBudget={project.budget_amount}
        currency={project.currency}
      />

      {/* Milestone Editor Modal */}
      {editingMilestone && (
        <MilestoneEditorModal
          isOpen={Boolean(editingMilestone)}
          onClose={() => setEditingMilestone(null)}
          milestone={editingMilestone}
          onSave={handleSaveMilestoneEdit}
        />
      )}
    </div>
  );
};
