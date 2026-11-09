import { User } from './auth';

export type MilestoneStatus =
  | 'not_started'
  | 'in_progress'
  | 'submitted'
  | 'revision_requested'
  | 'approved';

export type SubmissionStatus = 'draft' | 'submitted' | 'revision_requested' | 'approved';

export type AIReviewStatus = 'pending' | 'completed' | 'failed';

export type ClientSubmissionDecision = 'approved' | 'revision_requested';

export type CriterionEvaluationStatus =
  | 'met'
  | 'partially_met'
  | 'not_demonstrated'
  | 'unable_to_assess';

export interface SubmissionEvidence {
  id: string;
  submission_id: string;
  uploaded_by_id: string;
  original_filename: string;
  media_type: string;
  file_size_bytes: number;
  sha256_hash: string;
  created_at: string;
}

export interface CriterionEvaluation {
  criterion_id: number;
  criterion_text: string;
  status: CriterionEvaluationStatus;
  explanation: string;
  supporting_evidence_ids: string[];
  missing_information?: string | null;
}

export interface AISubmissionReview {
  id: string;
  submission_id: string;
  review_version: number;
  overall_summary: string;
  evaluation_results: CriterionEvaluation[];
  identified_gaps: string[];
  recommendations: string[];
  limitations: string[];
  areas_for_human_verification: string[];
  model_name: string | null;
  status: string;
  raw_error?: string | null;
  created_at: string;
}

export interface ClientSubmissionReview {
  id: string;
  submission_id: string;
  reviewer_user_id: string;
  decision: ClientSubmissionDecision;
  comment: string | null;
  created_at: string;
  reviewer: User;
}

export interface MilestoneSubmission {
  id: string;
  milestone_id: string;
  submitted_by_id: string;
  attempt_number: number;
  description: string;
  notes: string | null;
  demonstration_url: string | null;
  acceptance_criteria_snapshot: string[];
  status: SubmissionStatus;
  ai_review_status: AIReviewStatus;
  submitted_at: string | null;
  created_at: string;
  updated_at: string;
  submitted_by: User;
  evidence: SubmissionEvidence[];
  ai_reviews: AISubmissionReview[];
  client_reviews: ClientSubmissionReview[];
}

export interface CreateSubmissionInput {
  description: string;
  notes?: string;
  demonstration_url?: string;
}

export interface ClientReviewInput {
  decision: ClientSubmissionDecision;
  comment?: string;
}

export interface MilestoneSubmissionListResponse {
  submissions: MilestoneSubmission[];
  total: number;
}

