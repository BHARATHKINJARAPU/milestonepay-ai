import { User } from './auth';

export type ProjectStatus = 'draft' | 'active' | 'completed' | 'archived';
export type MemberRole = 'client' | 'freelancer';

export interface ProjectMember {
  id: string;
  project_id: string;
  user_id: string;
  role: MemberRole;
  joined_at: string;
  user: User;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  budget_amount: string | number;
  currency: string;
  deadline: string | null;
  status: ProjectStatus;
  created_by_id: string;
  created_at: string;
  updated_at: string;
  members: ProjectMember[];
}

export interface ProjectCreateInput {
  title: string;
  description: string;
  budget_amount: number;
  currency: string;
  deadline?: string | null;
}

export interface ProjectUpdateInput {
  title?: string;
  description?: string;
  budget_amount?: number;
  currency?: string;
  deadline?: string | null;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}
