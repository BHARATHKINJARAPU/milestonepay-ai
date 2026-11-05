import React, { useEffect, useState } from 'react';
import { useParams, Link, useOutletContext } from 'react-router-dom';
import { 
  ArrowLeft, 
  Calendar, 
  DollarSign, 
  Edit3, 
  CheckCircle2, 
  Users, 
  Building2, 
  Briefcase, 
  AlertCircle, 
  Loader2, 
  Archive,
  PlayCircle
} from 'lucide-react';
import { DashboardHeader } from '../../components/dashboard/DashboardHeader';
import { CollaboratorForm } from '../../components/projects/CollaboratorForm';
import { ProjectForm } from '../../components/projects/ProjectForm';
import { useAuth } from '../../context/AuthContext';
import { getProject, updateProject, updateProjectStatus } from '../../lib/api';
import { Project, ProjectCreateInput, ProjectStatus, ProjectUpdateInput } from '../../types/project';

interface OutletContextType {
  onOpenMobileMenu: () => void;
}

export const ProjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const { onOpenMobileMenu } = useOutletContext<OutletContextType>();

  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusActionLoading, setStatusActionLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  const fetchProjectDetails = async () => {
    if (!id) return;
    setIsLoading(true);
    try {
      const data = await getProject(id);
      setProject(data);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to retrieve project details');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjectDetails();
  }, [id]);

  if (isLoading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center text-slate-400 space-y-3 font-mono text-xs">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        <span>Loading project details...</span>
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
          className="inline-flex items-center gap-2 text-xs font-semibold text-blue-400 hover:text-blue-300"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Projects</span>
        </Link>
      </div>
    );
  }

  const isCreator = project.created_by_id === user?.id;
  const clientMember = project.members.find(m => m.role === 'client');
  const freelancerMember = project.members.find(m => m.role === 'freelancer');

  const handleStatusChange = async (targetStatus: ProjectStatus) => {
    setStatusActionLoading(true);
    setErrorMessage(null);
    try {
      const updated = await updateProjectStatus(project.id, targetStatus);
      setProject(updated);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Status update failed.');
    } finally {
      setStatusActionLoading(false);
    }
  };

  const handleEditSubmit = async (values: ProjectCreateInput | ProjectUpdateInput) => {
    setErrorMessage(null);
    try {
      const updated = await updateProject(project.id, values as ProjectUpdateInput);
      setProject(updated);
      setIsEditing(false);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Project update failed.');
    }
  };

  const getStatusBadge = (status: ProjectStatus) => {
    switch (status) {
      case 'active':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'completed':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'archived':
        return 'text-slate-400 bg-slate-800 border-slate-700';
      case 'draft':
      default:
        return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    }
  };

  return (
    <div>
      <DashboardHeader
        title={project.title}
        subtitle={`Project ID: ${project.id}`}
        onOpenMobileMenu={onOpenMobileMenu}
        showCreateAction={true}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-8 space-y-8">
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

        {/* Project Meta Banner */}
        <div className="p-6 sm:p-8 rounded-3xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <span className={`text-xs font-mono px-3 py-1 rounded-full uppercase tracking-wider font-semibold border ${getStatusBadge(project.status)}`}>
                Status: {project.status}
              </span>
              {isCreator && (
                <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  Project Creator
                </span>
              )}
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {project.title}
            </h2>
            <div className="flex flex-wrap items-center gap-6 text-xs text-slate-400 pt-1">
              <div className="flex items-center gap-1.5">
                <DollarSign className="w-4 h-4 text-emerald-400" />
                <span className="font-semibold text-white">
                  {project.currency} {Number(project.budget_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-slate-400" />
                <span>Deadline: {project.deadline || 'No target date set'}</span>
              </div>
              <div className="flex items-center gap-1.5 font-mono text-[11px] text-slate-500">
                <span>Created: {new Date(project.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          {/* Creator Status Actions & Edit Button */}
          {isCreator && (
            <div className="flex flex-wrap items-center gap-2 pt-4 md:pt-0 border-t md:border-t-0 border-slate-800">
              <button
                type="button"
                onClick={() => setIsEditing(!isEditing)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all flex items-center gap-1.5"
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>{isEditing ? 'Cancel Edit' : 'Edit Details'}</span>
              </button>

              {/* Status Transition buttons based on current state */}
              {project.status === 'draft' && (
                <button
                  type="button"
                  disabled={statusActionLoading}
                  onClick={() => handleStatusChange('active')}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white shadow-md shadow-emerald-600/20 transition-all flex items-center gap-1.5 disabled:opacity-50"
                >
                  <PlayCircle className="w-3.5 h-3.5" />
                  <span>Activate Project</span>
                </button>
              )}

              {project.status === 'active' && (
                <button
                  type="button"
                  disabled={statusActionLoading}
                  onClick={() => handleStatusChange('completed')}
                  className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-md shadow-blue-600/20 transition-all flex items-center gap-1.5 disabled:opacity-50"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Mark Completed</span>
                </button>
              )}

              {project.status !== 'archived' && (
                <button
                  type="button"
                  disabled={statusActionLoading}
                  onClick={() => handleStatusChange('archived')}
                  className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs font-semibold text-slate-400 border border-slate-800 transition-all flex items-center gap-1.5 disabled:opacity-50"
                >
                  <Archive className="w-3.5 h-3.5" />
                  <span>Archive</span>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Edit Form Modal/Drawer if isEditing */}
        {isEditing && (
          <div className="p-6 sm:p-8 rounded-3xl bg-slate-900/90 border border-blue-500/30 space-y-4">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider font-mono">
              Edit Project Details
            </h3>
            <ProjectForm
              initialValues={{
                title: project.title,
                description: project.description,
                budget_amount: project.budget_amount,
                currency: project.currency,
                deadline: project.deadline,
              }}
              onSubmit={handleEditSubmit}
              submitLabel="Save Changes"
            />
          </div>
        )}

        {/* 2-Column Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Scope & Description */}
          <div className="lg:col-span-7 space-y-6">
            <div className="p-6 sm:p-8 rounded-3xl bg-slate-900/60 border border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider font-mono">
                Project Scope & Deliverables
              </h3>
              <p className="text-sm text-slate-300 whitespace-pre-line leading-relaxed">
                {project.description}
              </p>
            </div>

            {/* AI Milestones placeholder for next phase */}
            <div className="p-6 rounded-3xl bg-slate-900/40 border border-dashed border-slate-800 text-center space-y-2">
              <span className="text-xs font-mono text-indigo-400 font-semibold uppercase">
                Phase 3 Integration Point
              </span>
              <h4 className="text-sm font-semibold text-white">AI Milestone Generation Engine</h4>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Once agreed by both the Client and Freelancer, AI will parse the description into structured milestone items and deliverable acceptance criteria.
              </p>
            </div>
          </div>

          {/* Right Column: Members & Collaboration */}
          <div className="lg:col-span-5 space-y-6">
            {/* Membership Details */}
            <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2 text-white text-sm font-semibold">
                  <Users className="w-4 h-4 text-blue-400" />
                  <span>Project Members</span>
                </div>
                <span className="text-[11px] font-mono text-slate-400">{project.members.length} / 2 Members</span>
              </div>

              {/* Client Card */}
              <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500">Client</span>
                    <h5 className="text-xs font-semibold text-white">
                      {clientMember ? clientMember.user.full_name : 'No Client Linked'}
                    </h5>
                    <p className="text-[11px] text-slate-400 font-mono">
                      {clientMember ? clientMember.user.email : 'Awaiting assignment'}
                    </p>
                  </div>
                </div>
                {clientMember && project.created_by_id === clientMember.user_id && (
                  <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
                    Creator
                  </span>
                )}
              </div>

              {/* Freelancer Card */}
              <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                    <Briefcase className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500">Freelancer</span>
                    <h5 className="text-xs font-semibold text-white">
                      {freelancerMember ? freelancerMember.user.full_name : 'No Freelancer Linked'}
                    </h5>
                    <p className="text-[11px] text-slate-400 font-mono">
                      {freelancerMember ? freelancerMember.user.email : 'Awaiting assignment'}
                    </p>
                  </div>
                </div>
                {freelancerMember && project.created_by_id === freelancerMember.user_id && (
                  <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
                    Creator
                  </span>
                )}
              </div>
            </div>

            {/* Add Collaborator Form (if missing member and user is creator) */}
            {isCreator && project.members.length < 2 && (
              <CollaboratorForm
                project={project}
                onCollaboratorAdded={(updated) => setProject(updated)}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
