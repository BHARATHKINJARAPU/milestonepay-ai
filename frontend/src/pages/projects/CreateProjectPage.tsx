import React, { useState } from 'react';
import { useNavigate, Link, useOutletContext } from 'react-router-dom';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import { DashboardHeader } from '../../components/dashboard/DashboardHeader';
import { ProjectForm } from '../../components/projects/ProjectForm';
import { createProject } from '../../lib/api';
import { ProjectCreateInput, ProjectUpdateInput } from '../../types/project';

interface OutletContextType {
  onOpenMobileMenu: () => void;
}

export const CreateProjectPage: React.FC = () => {
  const navigate = useNavigate();
  const { onOpenMobileMenu } = useOutletContext<OutletContextType>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleCreate = async (values: ProjectCreateInput | ProjectUpdateInput) => {
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const created = await createProject(values as ProjectCreateInput);
      navigate(`/projects/${created.id}`);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to create project');
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <DashboardHeader
        title="Create New Project"
        subtitle="Define project scope, budget, and target deliverables"
        onOpenMobileMenu={onOpenMobileMenu}
        showCreateAction={false}
      />

      <div className="max-w-3xl mx-auto px-4 sm:px-8 py-8 space-y-6">
        <Link
          to="/projects"
          className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Projects</span>
        </Link>

        {errorMessage && (
          <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-900/60 text-xs text-rose-300 flex items-center gap-3">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-8 backdrop-blur-xl shadow-2xl space-y-6">
          <div className="pb-4 border-b border-slate-800">
            <h2 className="text-lg font-bold text-white tracking-tight">Project Information</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Enter your initial project scope. You can add a collaborator once the project is created.
            </p>
          </div>

          <ProjectForm
            onSubmit={handleCreate}
            submitLabel="Create Project & Proceed"
            isSubmitting={isSubmitting}
          />
        </div>
      </div>
    </div>
  );
};
