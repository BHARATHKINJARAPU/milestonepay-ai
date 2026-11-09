import React, { useEffect, useState } from 'react';
import { useParams, Link, useOutletContext } from 'react-router-dom';
import { AlertCircle, ArrowLeft, Loader2 } from 'lucide-react';
import { DashboardHeader } from '../../components/dashboard/DashboardHeader';
import { PaymentConfirmation } from '../../components/payments/PaymentConfirmation';
import { getPayment } from '../../lib/api';
import { Payment } from '../../types/payment';

interface OutletContextType {
  onOpenMobileMenu: () => void;
}

export const PaymentResultPage: React.FC = () => {
  const { paymentId } = useParams<{ paymentId: string }>();
  const { onOpenMobileMenu } = useOutletContext<OutletContextType>();

  const [payment, setPayment] = useState<Payment | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadData = async () => {
    if (!paymentId) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await getPayment(paymentId);
      setPayment(data);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to retrieve payment receipt.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [paymentId]);

  if (isLoading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center text-slate-400 space-y-3 font-mono text-xs">
        <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
        <span>Loading transaction receipt...</span>
      </div>
    );
  }

  if (errorMessage || !payment) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-900/60 text-xs text-rose-300 flex items-center justify-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{errorMessage || 'Payment record not found.'}</span>
        </div>
        <Link
          to="/payments"
          className="inline-flex items-center gap-2 text-xs font-semibold text-cyan-400 hover:text-cyan-300"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Go to Payment History</span>
        </Link>
      </div>
    );
  }

  const projectTitle = payment.project?.title || (payment.provider_metadata?.project_title as string) || 'Project';
  const milestoneTitle = payment.milestone?.title || (payment.provider_metadata?.milestone_title as string) || 'Approved Deliverable';

  return (
    <div className="space-y-8 pb-16 max-w-3xl mx-auto">
      <DashboardHeader
        title="Payment Confirmation Receipt"
        subtitle={`Transaction reference #${payment.id.slice(0, 8)}`}
        onOpenMobileMenu={onOpenMobileMenu}
      />

      <PaymentConfirmation
        payment={payment}
        projectTitle={projectTitle}
        milestoneTitle={milestoneTitle}
      />
    </div>
  );
};
