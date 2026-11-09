export interface ProjectActivity {
  id: string;
  project_id: string;
  actor_user_id?: string | null;
  actor_name?: string | null;
  activity_type: string;
  title: string;
  description?: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface ProjectActivityListResponse {
  activities: ProjectActivity[];
  total: number;
}

