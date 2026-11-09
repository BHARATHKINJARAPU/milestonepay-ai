import React from 'react';
import { CreditCard, DollarSign, ShieldCheck, Zap } from 'lucide-react';
import { DashboardPaymentsSummary } from '../../types/analytics';

interface FinancialOverviewCardProps {
  payments: DashboardPaymentsSummary;
  role: 'client' | 'freelancer';
}

export const FinancialOverviewCard: React.FC<FinancialOverviewCardProps> = ({
  payments,
  role,
}) => {
  // Extract totals (primary currency USD or first available)
  const paypalCompleted = payments.completed_paypal_by_currency[0]?.amount || 0;
  const mockCompleted = payments.completed_mock_by_currency[0]?.amount || 0;
  const approvedValue = payments.approved_value_by_currency[0]?.amount || 0;
  const pendingValue = payments.pending_by_currency[0]?.amount || 0;
  const currency = payments.completed_paypal_by_currency[0]?.currency || 'USD';

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-6">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <DollarSign className="h-4 w-4 text-emerald-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-white font-mono">
            {role === 'client' ? 'Financial Commitments & Settlements' : 'Milestone Earnings & Settlements'}
          </h3>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/40 px-2.5 py-0.5 rounded-full">
          {currency} Base
        </span>
      </div>

      {/* Grid of Monetary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Real PayPal Completed */}
        <div className="rounded-2xl border border-blue-500/30 bg-blue-950/20 p-4 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono uppercase tracking-wider text-blue-300">
              PayPal Sandbox Settled
            </span>
            <ShieldCheck className="h-3.5 w-3.5 text-blue-400" />
          </div>
          <div className="font-mono text-xl font-bold text-white">
            ${paypalCompleted.toFixed(2)}
          </div>
          <p className="text-[10px] text-slate-400">
            Verified REST API v2 captures
          </p>
        </div>

        {/* Mock Simulated Completed */}
        <div className="rounded-2xl border border-amber-500/30 bg-amber-950/20 p-4 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono uppercase tracking-wider text-amber-300">
              Simulated Mock Settled
            </span>
            <Zap className="h-3.5 w-3.5 text-amber-400" />
          </div>
          <div className="font-mono text-xl font-bold text-amber-200">
            ${mockCompleted.toFixed(2)}
          </div>
          <p className="text-[10px] text-slate-400">
            Test / development provider
          </p>
        </div>

        {/* Approved Awaiting Payment */}
        <div className="rounded-2xl border border-cyan-500/30 bg-cyan-950/20 p-4 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-300">
              {role === 'client' ? 'Approved Awaiting Checkout' : 'Approved Value'}
            </span>
            <CreditCard className="h-3.5 w-3.5 text-cyan-400" />
          </div>
          <div className="font-mono text-xl font-bold text-cyan-200">
            ${approvedValue.toFixed(2)}
          </div>
          <p className="text-[10px] text-slate-400">
            {role === 'client' ? 'Ready for PayPal or Mock release' : 'Authorized by client for payment'}
          </p>
        </div>

        {/* Pending In-Flight Payments */}
        <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
              In-Flight / Pending
            </span>
            <span className="text-[10px] font-mono text-slate-500">
              {payments.failed_count} failed
            </span>
          </div>
          <div className="font-mono text-xl font-bold text-slate-300">
            ${pendingValue.toFixed(2)}
          </div>
          <p className="text-[10px] text-slate-500">
            Orders created awaiting authorization
          </p>
        </div>
      </div>

      {/* Transparent Disclaimer Notice */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-950/40 p-3 text-[11px] text-slate-400 flex items-center justify-between">
        <span>
          <strong>Platform Architecture:</strong> PayPal Sandbox transactions settle into the configured merchant seller account. Mock payments remain strictly simulated and separated.
        </span>
        <span className="font-mono text-[10px] text-slate-500 whitespace-nowrap ml-4">
          Settled transactions: {payments.completed_count}
        </span>
      </div>
    </div>
  );
};

