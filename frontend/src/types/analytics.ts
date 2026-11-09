export interface CurrencyAmount {
  currency: string;
  amount: number;
}

export interface DashboardProjectsSummary {
  total: number;
  active: number;
  completed: number;
  awaiting_review: number;
  attention_needed: number;
}

export interface DashboardMilestonesSummary {
  total: number;
  not_started: number;
  in_progress: number;
  submitted: number;
  revision_requested: number;
  approved: number;
}

export interface DashboardPaymentsSummary {
  total_budget_by_currency: CurrencyAmount[];
  approved_value_by_currency: CurrencyAmount[];
  completed_paypal_by_currency: CurrencyAmount[];
  completed_mock_by_currency: CurrencyAmount[];
  pending_by_currency: CurrencyAmount[];
  failed_count: number;
  completed_count: number;
}

export interface UpcomingDeadlineItem {
  milestone_id: string;
  milestone_title: string;
  project_id: string;
  project_title: string;
  deadline?: string | null;
  status: string;
  suggested_budget: number;
  currency: string;
}

export interface ReviewCenterItem {
  item_type: 'plan_review' | 'submission_review' | 'pending_payment';
  project_id: string;
  project_title: string;
  milestone_id?: string | null;
  milestone_title?: string | null;
  submission_id?: string | null;
  title: string;
  subtitle: string;
  action_url: string;
  created_at: string;
  amount?: number | null;
  currency?: string | null;
}

export interface CollaboratorOverviewItem {
  user_id: string;
  name: string;
  email: string;
  role: string;
  project_count: number;
  active_milestone_count: number;
  latest_project_title?: string | null;
}

export interface DashboardAnalytics {
  role: 'client' | 'freelancer';
  projects: DashboardProjectsSummary;
  milestones: DashboardMilestonesSummary;
  payments: DashboardPaymentsSummary;
  upcoming_deadlines: UpcomingDeadlineItem[];
  review_center: ReviewCenterItem[];
  collaborators: CollaboratorOverviewItem[];
}

export interface PaymentTrendsItem {
  date: string;
  currency: string;
  completed_paypal_amount: number;
  completed_mock_amount: number;
  count: number;
}

export interface PaymentAnalytics {
  payments_summary: DashboardPaymentsSummary;
  trends: PaymentTrendsItem[];
}

export interface ProjectAiSummary {
  project_id: string;
  generated_at: string;
  is_ai_generated: boolean;
  executive_summary: string;
  progress_assessment: string;
  key_accomplishments: string[];
  potential_risks: string[];
  recommended_next_steps: string[];
  metrics: {
    total_budget: number;
    currency: string;
    total_milestones: number;
    approved_milestones: number;
    submitted_milestones: number;
    in_progress_milestones: number;
    paid_milestones: number;
    completion_percentage: number;
    completed_payments: number;
    plan_status: string;
  };
}

