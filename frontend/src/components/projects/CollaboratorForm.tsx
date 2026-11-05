import React, { useState } from 'react';
import { UserPlus, Mail, Loader2, AlertCircle, CheckCircle2, Info } from 'lucide-react';
import { addProjectMember } from '../../lib/api';
import { Project } from '../../types/project';
import { useAuth } from '../../context/AuthContext';

interface CollaboratorFormProps {
  project: Project;
  onCollaboratorAdded: (updatedProject: Project) => void;
}

export const CollaboratorForm: React.FC<CollaboratorFormProps> = ({ project, onCollaboratorAdded }) => {
  const { user } = useAuth();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const expectedRole = user?.account_type === 'client' ? 'Freelancer' : 'Client';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!email.trim()) {
      setErrorMessage('Please enter an email address.');
      return;
    }

    setIsLoading(true);
    try {
      const updated = await addProjectMember(project.id, email.trim());
      setSuccessMessage(`Collaborator added to project successfully.`);
      setEmail('');
      onCollaboratorAdded(updated);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to add collaborator.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800 space-y-4">
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
          <UserPlus className="w-4 h-4" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-white">Add Project Collaborator</h4>
          <p className="text-xs text-slate-400">
            Link a registered {expectedRole} to this project by their registered email.
          </p>
        </div>
      </div>

      {errorMessage && (
        <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-900/60 flex items-start gap-2.5 text-xs text-rose-300">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <span>{errorMessage}</span>
        </div>
      )}

      {successMessage && (
        <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-900/60 flex items-start gap-2.5 text-xs text-emerald-300">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          <span>{successMessage}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-500">
            <Mail className="h-4 w-4" />
          </div>
          <input
            type="email"
            required
            placeholder={`Enter ${expectedRole.toLowerCase()}'s registered email`}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="block w-full rounded-xl bg-slate-950 border border-slate-800 pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2.5 px-4 rounded-xl font-semibold text-white bg-blue-600 hover:bg-blue-500 transition-all text-xs flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Verifying & Linking Collaborator...</span>
            </>
          ) : (
            <>
              <UserPlus className="w-3.5 h-3.5" />
              <span>Add {expectedRole}</span>
            </>
          )}
        </button>
      </form>

      <div className="pt-2 border-t border-slate-800/80 flex items-start gap-2 text-[11px] text-slate-500">
        <Info className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
        <span>
          Note: Collaborator must already have a registered {expectedRole} account. Email invitations will be introduced in future development phases.
        </span>
      </div>
    </div>
  );
};
