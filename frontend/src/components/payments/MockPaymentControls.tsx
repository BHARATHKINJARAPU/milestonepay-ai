import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, Loader2, XCircle } from 'lucide-react';
import { Payment } from '../../types/payment';
import { mockConfirmPayment } from '../../lib/api';

interface MockPaymentControlsProps {
  payment: Payment;
  onPaymentUpdated: (updated: Payment) => void;
}

export const MockPaymentControls: React.FC<MockPaymentControlsProps> = ({
  payment,
  onPaymentUpdated,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleAction = async (outcome: 'success' | 'fail' | 'cancel') => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const updated = await mockConfirmPayment(payment.id, { outcome });
      onPaymentUpdated(updated);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Simulated payment action failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const isCompleted = payment.status === 'completed';

  return (
    <div className="rounded-2xl border border-amber-500/30 bg-amber-950/20 p-6 backdrop-blur-sm">
      {/* Prominent Simulated Banner */}
      <div className="flex items-center gap-2 rounded-xl bg-amber-950/60 border border-amber-500/40 p-3.5 text-amber-300">
        <AlertTriangle className="h-5 w-5 shrink-0 text-amber-400" />
        <div className="text-xs">
          <strong className="font-bold uppercase tracking-wider block">
            SIMULATED PAYMENT — NOT A REAL PAYPAL TRANSACTION
          </strong>
          <span className="text-amber-200/80">
            Running in local development mock provider mode. Use buttons below to simulate realistic transaction outcomes.
          </span>
        </div>
      </div>

      {errorMsg && (
        <div className="mt-4 rounded-xl border border-rose-500/40 bg-rose-950/50 p-3 text-xs text-rose-300">
          {errorMsg}
        </div>
      )}

      {/* Action Buttons */}
      {!isCompleted ? (
        <div className="mt-6 space-y-3">
          <button
            type="button"
            disabled={isLoading}
            onClick={() => handleAction('success')}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-emerald-950/50 hover:bg-emerald-500 disabled:opacity-50 transition-all cursor-pointer"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <CheckCircle2 className="h-4 w-4" />
            )}
            <span>Simulate Successful Payment Release</span>
          </button>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <button
              type="button"
              disabled={isLoading}
              onClick={() => handleAction('fail')}
              className="flex items-center justify-center gap-2 rounded-xl border border-rose-800/80 bg-rose-950/30 px-4 py-2.5 text-xs font-semibold text-rose-300 hover:bg-rose-950/60 disabled:opacity-50 transition-all"
            >
              <AlertTriangle className="h-3.5 w-3.5" />
              <span>Simulate Provider Failure</span>
            </button>

            <button
              type="button"
              disabled={isLoading}
              onClick={() => handleAction('cancel')}
              className="flex items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800/60 px-4 py-2.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 disabled:opacity-50 transition-all"
            >
              <XCircle className="h-3.5 w-3.5" />
              <span>Simulate User Cancellation</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="mt-6 rounded-xl border border-emerald-500/30 bg-emerald-950/40 p-4 text-center">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <h4 className="mt-2 text-sm font-bold text-white">Simulated Payment Finished</h4>
          <p className="mt-1 text-xs text-slate-400">
            Transaction is finalized with capture ID: <span className="font-mono text-emerald-300">{payment.provider_capture_id}</span>
          </p>
        </div>
      )}
    </div>
  );
};
