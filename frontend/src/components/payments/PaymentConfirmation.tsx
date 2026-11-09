import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, History } from 'lucide-react';
import { Payment } from '../../types/payment';

interface PaymentConfirmationProps {
  payment: Payment;
  projectTitle?: string;
  milestoneTitle?: string;
}

export const PaymentConfirmation: React.FC<PaymentConfirmationProps> = ({
  payment,
  projectTitle = 'Project Milestone',
  milestoneTitle = 'Approved Deliverable',
}) => {
  const isMock = payment.provider === 'mock';

  return (
    <div className="rounded-3xl border border-emerald-500/30 bg-slate-900/80 p-8 backdrop-blur-md space-y-8 shadow-2xl shadow-emerald-950/20">
      {/* Success Badge & Title */}
      <div className="text-center space-y-3">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-emerald-500/20 to-cyan-500/20 border border-emerald-500/40 text-emerald-400">
          <CheckCircle2 className="h-8 w-8" />
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Payment Successfully Released
        </h2>
        <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
          The agreed funds for this milestone have been authorized, captured, and permanently recorded in the immutable audit trail.
        </p>
      </div>

      {/* Simulated Notice if Mock */}
      {isMock && (
        <div className="rounded-xl border border-amber-500/40 bg-amber-950/40 p-3.5 text-center text-xs font-semibold text-amber-300">
          SIMULATED PAYMENT — NOT A REAL PAYPAL TRANSACTION
        </div>
      )}

      {/* Financial Receipt Card */}
      <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-6 space-y-4">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Transaction Scope</div>
            <div className="text-sm font-bold text-white mt-0.5">{projectTitle} &bull; {milestoneTitle}</div>
          </div>
          <div className="text-right">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Released Amount</div>
            <div className="font-mono text-xl font-extrabold text-emerald-400">
              {payment.currency} {Number(payment.amount).toFixed(2)}
            </div>
          </div>
        </div>

        {/* Audit Details Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
          <div>
            <span className="text-slate-500 block">Internal Payment ID:</span>
            <span className="text-slate-300 break-all">{payment.id}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Provider:</span>
            <span className={isMock ? 'text-amber-400 font-bold' : 'text-blue-400 font-bold'}>
              {isMock ? 'Mock Provider (Simulated)' : 'PayPal Sandbox REST API v2'}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block">Provider Order ID:</span>
            <span className="text-cyan-300">{payment.provider_order_id || 'N/A'}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Provider Capture ID:</span>
            <span className="text-emerald-300 font-bold">{payment.provider_capture_id || 'N/A'}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Settled Timestamp:</span>
            <span className="text-slate-300">
              {payment.completed_at ? new Date(payment.completed_at).toLocaleString() : 'Just now'}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block">Status:</span>
            <span className="text-emerald-400 font-bold uppercase">{payment.status}</span>
          </div>
        </div>
      </div>

      {/* Navigation Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
        <Link
          to={`/projects/${payment.project_id}/milestones`}
          className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 px-6 py-3 text-xs font-semibold text-white shadow-lg shadow-cyan-950/40 hover:from-cyan-400 hover:to-indigo-500 transition-all"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Return to Milestone Workspace</span>
        </Link>

        <Link
          to="/payments"
          className="inline-flex w-full sm:w-auto items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-6 py-3 text-xs font-semibold text-slate-200 hover:bg-slate-700 hover:text-white transition-all"
        >
          <History className="h-4 w-4" />
          <span>View All Payment History</span>
        </Link>
      </div>
    </div>
  );
};
