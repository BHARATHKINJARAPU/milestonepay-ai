import React, { useEffect, useState } from 'react';
import { History, Loader2, RefreshCw } from 'lucide-react';
import { ProjectActivity } from '../../types/activity';
import { getProjectActivities } from '../../lib/api';
import { ActivityItem } from './ActivityItem';

interface ProjectActivityTimelineProps {
  projectId: string;
}

export const ProjectActivityTimeline: React.FC<ProjectActivityTimelineProps> = ({
  projectId,
}) => {
  const [activities, setActivities] = useState<ProjectActivity[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadActivities = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await getProjectActivities(projectId, { limit: 30 });
      if (data) {
        setActivities(data.activities);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to load activities.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      loadActivities();
    }
  }, [projectId]);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <History className="h-4 w-4 text-cyan-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-white font-mono">
            Project Activity Timeline
          </h3>
          <span className="text-xs text-slate-500 font-mono">({activities.length})</span>
        </div>

        <button
          type="button"
          onClick={loadActivities}
          disabled={isLoading}
          className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          title="Refresh activities"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-10 text-slate-500">
          <Loader2 className="h-6 w-6 animate-spin text-cyan-400" />
        </div>
      ) : errorMessage ? (
        <div className="rounded-xl border border-rose-500/20 bg-rose-950/20 p-4 text-xs text-rose-300">
          {errorMessage}
        </div>
      ) : activities.length === 0 ? (
        <div className="py-8 text-center text-xs text-slate-500">
          No activities recorded for this project yet.
        </div>
      ) : (
        <div className="relative pl-3 space-y-4 before:absolute before:left-6.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
          {activities.map((act) => (
            <ActivityItem key={act.id} activity={act} />
          ))}
        </div>
      )}
    </div>
  );
};

