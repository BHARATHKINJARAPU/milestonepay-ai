import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link, useOutletContext } from 'react-router-dom';
import {
  AlertCircle,
  ArrowLeft,
  CreditCard,
  Loader2,
} from 'lucide-react';
import { DashboardHeader } from '../../components/dashboard/DashboardHeader';
import { PaymentSummary } from '../../components/payments/PaymentSummary';
import { PayPalCheckout } from '../../components/payments/PayPalCheckout';
import { MockPaymentControls } from '../../components/payments/MockPaymentControls';
import {
  checkPaymentEligibility,
  createMilestonePayment,
  getMilestonePlans,
  getPayment,
  getProject,
} from '../../lib/api';
import { Milestone } from '../../types/milestone';
import { Project } from '../../types/project';
import { Payment, PaymentEligibility, PaymentProvider } from '../../types/payment';

interface OutletContextType {
  onOpenMobileMenu: () => void;
}

export const MilestonePaymentPage: React.FC = () => {
  const { projectId, milestoneId } = useParams<{ projectId: string; milestoneId: string }>();
  const navigate = useNavigate();
  const { onOpenMobileMenu } = useOutletContext<OutletContextType>();

  const [project, setProject] = useState<Project | null>(null);
  const [milestone, setMilestone] = useState<Milestone | null>(null);
  const [eligibility, setEligibility] = useState<PaymentEligibility | null>(null);
  const [activePayment, setActivePayment] = useState<Payment | null>(null);

  const [selectedProvider, setSelectedProvider] = useState<PaymentProvider>('paypal');
  const [isLoading, setIsLoading] = useState(true);
  const [isCreatingPayment, setIsCreatingPayment] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadData = async () => {
    if (!projectId || !milestoneId) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [projData, eligData, plansData] = await Promise.all([
        getProject(projectId),
        checkPaymentEligibility(projectId, milestoneId),
        getMilestonePlans(projectId),
      ]);

      setProject(projData);
      setEligibility(eligData);

      // Find milestone details from agreed plan
      const agreedPlan = plansData.plans.find((p) => p.status === 'agreed') || plansData.plans[0];
      if (agreedPlan) {
        const found = agreedPlan.milestones.find((m) => m.id === milestoneId);
        if (found) setMilestone(found);
      }

      // If active payment already initiated, initialize it
      if (eligData.active_payment_id) {
        const existing = await getPayment(eligData.active_payment_id);
        setActivePayment(existing);
        setSelectedProvider(existing.provider);
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to initialize payment checkout.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId, milestoneId]);

  // Initiate order creation when ready
  const handleInitiatePayment = async (provider: PaymentProvider) => {
    if (!projectId || !milestoneId) return;
    setIsCreatingPayment(true);
    setErrorMessage(null);
    try {
      const newPayment = await createMilestonePayment(projectId, milestoneId, { provider });
      setActivePayment(newPayment);
      setSelectedProvider(provider);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to create payment order.');
    } finally {
      setIsCreatingPayment(false);
    }
  };

  const handlePaymentCompleted = (updated: Payment) => {
    setActivePayment(updated);
    if (updated.status === 'completed') {
      navigate(`/payments/${updated.id}/result`);
    }
  };

  if (isLoading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center text-slate-400 space-y-3 font-mono text-xs">
        <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
        <span>Loading checkout session...</span>
      </div>
    );
  }

  if (errorMessage || !project || !milestone) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-900/60 text-xs text-rose-300 flex items-center justify-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{errorMessage || 'Payment details could not be found.'}</span>
        </div>
        <Link
          to={`/projects/${projectId}/milestones`}
          className="inline-flex items-center gap-2 text-xs font-semibold text-cyan-400 hover:text-cyan-300"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Milestone Workspace</span>
        </Link>
      </div>
    );
  }

  const freelancer = project.members.find((m) => m.role === 'freelancer')?.user;

  return (
    <div className="space-y-8 pb-16 max-w-4xl mx-auto">
      {/* Top Header */}
      <DashboardHeader
        title="Milestone Payment Checkout"
        subtitle={`Release payment for approved milestone #${milestone.sequence_number}`}
        onOpenMobileMenu={onOpenMobileMenu}
      />

      {/* Navigation Breadcrumb */}
      <div className="flex items-center gap-4">
        <Link
          to={`/projects/${projectId}/milestones`}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white hover:border-slate-700 transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Return to Milestones
        </Link>
      </div>

      {/* Ineligibility Warning if not eligible */}
      {eligibility && !eligibility.eligible && (
        <div className="rounded-2xl border border-rose-500/40 bg-rose-950/30 p-6 space-y-3">
          <div className="flex items-center gap-2 text-rose-400 font-bold text-sm">
            <AlertCircle className="h-5 w-5" />
            <span>Milestone Not Eligible for Payment</span>
          </div>
          <p className="text-xs text-rose-200/80 leading-relaxed">
            {eligibility.reason}
          </p>
          {eligibility.completed_payment_id && (
            <Link
              to={`/payments/${eligibility.completed_payment_id}/result`}
              className="inline-flex items-center gap-2 rounded-xl bg-slate-800 border border-slate-700 px-4 py-2 text-xs font-semibold text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              <span>View Completed Payment Receipt</span>
            </Link>
          )}
        </div>
      )}

      {/* Payment Summary */}
      <PaymentSummary
        project={project}
        milestone={milestone}
        freelancerName={freelancer?.full_name}
        paymentStatus={activePayment?.status}
      />

      {/* Eligible Payment Flow */}
      {eligibility && eligibility.eligible && (
        <div className="space-y-6">
          {/* Provider Selection (When not yet created) */}
          {!activePayment && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 font-mono">
                Select Payment Method
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* PayPal Sandbox Option */}
                <button
                  type="button"
                  onClick={() => setSelectedProvider('paypal')}
                  className={`flex flex-col items-start p-4 rounded-xl border text-left transition-all cursor-pointer ${
                    selectedProvider === 'paypal'
                      ? 'border-blue-500/80 bg-blue-950/40 shadow-lg shadow-blue-950/30'
                      : 'border-slate-800 bg-slate-950/50 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between w-full">
                    <span className="font-bold text-sm text-white">PayPal Sandbox</span>
                    <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                      JS SDK v6
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                    Official PayPal Sandbox checkout integration. Authenticate with a Sandbox personal account to test end-to-end capture.
                  </p>
                </button>

                {/* Simulated Mock Provider Option */}
                <button
                  type="button"
                  onClick={() => setSelectedProvider('mock')}
                  className={`flex flex-col items-start p-4 rounded-xl border text-left transition-all cursor-pointer ${
                    selectedProvider === 'mock'
                      ? 'border-amber-500/80 bg-amber-950/40 shadow-lg shadow-amber-950/30'
                      : 'border-slate-800 bg-slate-950/50 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between w-full">
                    <span className="font-bold text-sm text-white">Simulated Mock Provider</span>
                    <span className="text-[10px] font-mono text-amber-300 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/40">
                      TEST / DEV
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                    Zero-credential simulated checkout. Test successful capture, simulated failure, or cancellation instantly.
                  </p>
                </button>
              </div>

              {/* Initiate Button */}
              <div className="pt-2">
                <button
                  type="button"
                  disabled={isCreatingPayment}
                  onClick={() => handleInitiatePayment(selectedProvider)}
                  className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 px-6 py-3.5 text-xs font-bold text-white shadow-lg shadow-cyan-950/50 hover:from-cyan-400 hover:to-indigo-500 disabled:opacity-50 transition-all cursor-pointer"
                >
                  {isCreatingPayment ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <CreditCard className="h-4 w-4" />
                  )}
                  <span>
                    Proceed with {selectedProvider === 'paypal' ? 'PayPal Sandbox' : 'Simulated Mock Checkout'}
                  </span>
                </button>
              </div>
            </div>
          )}

          {/* Active Provider Checkout Render */}
          {activePayment && (
            <div>
              {activePayment.provider === 'paypal' ? (
                <PayPalCheckout
                  payment={activePayment}
                  onPaymentUpdated={handlePaymentCompleted}
                />
              ) : (
                <MockPaymentControls
                  payment={activePayment}
                  onPaymentUpdated={handlePaymentCompleted}
                />
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
