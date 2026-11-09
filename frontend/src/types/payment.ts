import { User } from './auth';

export type PaymentProvider = 'mock' | 'paypal';

export type PaymentStatus =
  | 'pending'
  | 'order_created'
  | 'payer_approved'
  | 'processing'
  | 'completed'
  | 'failed'
  | 'cancelled';

export type PaymentEventSource = 'mock' | 'paypal_api' | 'paypal_webhook';

export type MilestonePaymentStatus = 'unpaid' | 'pending' | 'completed';

export interface PaymentEvent {
  id: string;
  payment_id: string;
  event_type: string;
  provider_event_id?: string | null;
  event_source: PaymentEventSource;
  event_payload: Record<string, unknown>;
  processed: boolean;
  created_at: string;
}

export interface Payment {
  id: string;
  milestone_id: string;
  project_id: string;
  client_user_id: string;
  freelancer_user_id: string;
  provider: PaymentProvider;
  provider_order_id?: string | null;
  provider_capture_id?: string | null;
  amount: number | string;
  currency: string;
  status: PaymentStatus;
  payment_method?: string | null;
  failure_reason?: string | null;
  provider_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
  client?: User;
  freelancer?: User;
  project?: { id: string; title: string };
  milestone?: { id: string; title: string };
  events?: PaymentEvent[];
}

export interface PaymentEligibility {
  eligible: boolean;
  reason?: string | null;
  amount: number | string;
  currency: string;
  payment_status: MilestonePaymentStatus;
  active_payment_id?: string | null;
  active_provider_order_id?: string | null;
  completed_payment_id?: string | null;
  provider: string;
}

export interface CreatePaymentPayload {
  provider?: PaymentProvider;
}

export interface MockConfirmPayload {
  outcome: 'success' | 'fail' | 'cancel';
}

export interface PaymentListResponse {
  payments: Payment[];
  total: number;
}

export type CheckoutStage =
  | 'buyer_approval_required'
  | 'buyer_approved'
  | 'capturing'
  | 'capture_pending'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface PaymentStatusCheck {
  payment_id: string;
  project_id: string;
  milestone_id: string;
  provider: PaymentProvider;
  provider_order_id?: string | null;
  provider_capture_id?: string | null;
  amount: number | string;
  currency: string;
  internal_status: PaymentStatus;
  stage: CheckoutStage | string;
  can_capture: boolean;
  provider_status?: string | null;
  approval_url?: string | null;
  payer_email?: string | null;
  payer_id?: string | null;
  failure_reason?: string | null;
  updated_at: string;
}
