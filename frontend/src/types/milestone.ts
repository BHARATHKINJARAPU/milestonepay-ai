import { User } from './auth';
import { MilestoneStatus } from './submission';
import { MilestonePaymentStatus } from './payment';

export type PlanStatus = 'draft' | 'pending_approval' | 'revision_requested' | 'agreed';
export type PlanGenerationSource = 'ai' | 'manual';
export type ReviewDecision = 'approved' | 'changes_requested';

export interface Milestone {
  id: string;
  plan_id: string;
  sequence_number: number;
  title: string;
  description: string;
  deliverables: string[];
  acceptance_criteria: string[];
  estimated_duration_days: number;
  start_date: string | null;
  due_date: string | null;
  budget_percentage: number | string;
  amount: number | string;
  currency: string;
  dependencies: number[];
  status?: MilestoneStatus;
  payment_status?: MilestonePaymentStatus;
  created_at: string;
  updated_at: string;
}

export interface MilestonePlanReview {
  id: string;
  plan_id: string;
  reviewer_user_id: string;
  reviewer_role: 'client' | 'freelancer';
  decision: ReviewDecision;
  comment: string | null;
  created_at: string;
  reviewer: User;
}

export interface MilestonePlan {
  id: string;
  project_id: string;
  version: number;
  status: PlanStatus;
  project_summary: string;
  total_amount: number | string;
  currency: string;
  assumptions: string[];
  clarifying_questions: string[];
  risks: string[];
  needs_clarification: boolean;
  generation_source: PlanGenerationSource;
  ai_model: string | null;
  created_by_id: string;
  created_at: string;
  updated_at: string;
  milestones: Milestone[];
  reviews: MilestonePlanReview[];
}

export interface GenerateMilestonePlanInput {
  additional_instructions?: string;
}

export interface MilestoneInput {
  id?: string;
  sequence_number: number;
  title: string;
  description: string;
  deliverables: string[];
  acceptance_criteria: string[];
  estimated_duration_days: number;
  budget_percentage: number;
  dependencies: number[];
}

export interface CreateManualPlanInput {
  project_summary: string;
  milestones: MilestoneInput[];
  assumptions?: string[];
  clarifying_questions?: string[];
  risks?: string[];
}

export interface UpdateMilestonePlanInput {
  project_summary?: string;
  assumptions?: string[];
  clarifying_questions?: string[];
  risks?: string[];
  milestones?: MilestoneInput[];
}

export interface MilestonePlanListResponse {
  plans: MilestonePlan[];
  total: number;
}

