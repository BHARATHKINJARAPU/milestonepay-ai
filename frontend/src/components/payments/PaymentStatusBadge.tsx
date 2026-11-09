import React from 'react';
import { AlertCircle, CheckCircle2, Clock, Loader2, XCircle } from 'lucide-react';
import { PaymentProvider, PaymentStatus } from '../../types/payment';

interface PaymentStatusBadgeProps {
  status: PaymentStatus;
  provider?: PaymentProvider;
  className?: string;
  showProvider?: boolean;
}

export const PaymentStatusBadge: React.FC<PaymentStatusBadgeProps> = ({
  status,
  provider,
  className = '',
  showProvider = false,
}) => {
  const getStatusConfig = (st: PaymentStatus) => {
    switch (st) {
      case 'completed':
        return {
          label: 'Payment Completed',
          icon: CheckCircle2,
          classes: 'bg-emerald-950/70 text-emerald-400 border-emerald-500/40 shadow-sm shadow-emerald-950/50',
        };
      case 'order_created':
        return {
          label: 'Order Initiated',
          icon: Clock,
          classes: 'bg-cyan-950/70 text-cyan-300 border-cyan-500/40',
        };
      case 'payer_approved':
      case 'processing':
        return {
          label: 'Processing Capture',
          icon: Loader2,
          classes: 'bg-blue-950/70 text-blue-300 border-blue-500/40 animate-pulse',
        };
      case 'failed':
        return {
          label: 'Payment Failed',
          icon: AlertCircle,
          classes: 'bg-rose-950/70 text-rose-300 border-rose-500/40',
        };
      case 'cancelled':
        return {
          label: 'Cancelled',
          icon: XCircle,
          classes: 'bg-slate-800 text-slate-400 border-slate-700',
        };
      case 'pending':
      default:
        return {
          label: 'Pending Checkout',
          icon: Clock,
          classes: 'bg-amber-950/70 text-amber-300 border-amber-500/40',
        };
    }
  };

  const config = getStatusConfig(status);
  const Icon = config.icon;

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <span
        className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold tracking-wide ${config.classes}`}
      >
        <Icon className={`h-3.5 w-3.5 ${status === 'processing' || status === 'payer_approved' ? 'animate-spin' : ''}`} />
        <span>{config.label}</span>
      </span>

      {showProvider && provider && (
        <span
          className={`rounded-md border px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider ${
            provider === 'paypal'
              ? 'border-blue-500/40 bg-blue-950/60 text-blue-300'
              : 'border-amber-500/40 bg-amber-950/60 text-amber-300'
          }`}
        >
          {provider === 'paypal' ? 'PayPal Sandbox' : 'Simulated (Mock)'}
        </span>
      )}
    </div>
  );
};
