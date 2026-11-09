import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { AlertCircle, CheckCircle2, DollarSign, Filter, Loader2, RefreshCw } from 'lucide-react';
import { DashboardHeader } from '../../components/dashboard/DashboardHeader';
import { PaymentHistoryTable } from '../../components/payments/PaymentHistoryTable';
import { getPayments } from '../../lib/api';
import { Payment } from '../../types/payment';

interface OutletContextType {
  onOpenMobileMenu: () => void;
}

export const PaymentHistoryPage: React.FC = () => {
  const { onOpenMobileMenu } = useOutletContext<OutletContextType>();

  const [payments, setPayments] = useState<Payment[]>([]);
  const [providerFilter, setProviderFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadPayments = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const params: any = {};
      if (providerFilter !== 'all') params.provider = providerFilter;
      if (statusFilter !== 'all') params.status = statusFilter;

      const res = await getPayments(params);
      setPayments(res.payments);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to retrieve payment history.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPayments();
  }, [providerFilter, statusFilter]);

  // Aggregate metrics
  const totalCompletedAmount = payments
    .filter((p) => p.status === 'completed')
    .reduce((sum, p) => sum + Number(p.amount), 0);

  const completedCount = payments.filter((p) => p.status === 'completed').length;
  const inProgressCount = payments.filter((p) => p.status === 'order_created' || p.status === 'processing').length;

  return (
    <div className="space-y-8 pb-16">
      <DashboardHeader
        title="Payment & Transaction History"
        subtitle="Audit logs of released milestone payments across PayPal Sandbox and Mock providers"
        onOpenMobileMenu={onOpenMobileMenu}
      />

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-5 backdrop-blur-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Funds Released</div>
          <div className="mt-2 flex items-baseline gap-1 font-mono text-2xl font-bold text-emerald-400">
            <DollarSign className="h-5 w-5" />
            {totalCompletedAmount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="mt-1 text-[11px] text-slate-500">Across all completed milestone payments</div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-5 backdrop-blur-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Completed Payments</div>
          <div className="mt-2 font-mono text-2xl font-bold text-white flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-emerald-400" />
            <span>{completedCount}</span>
          </div>
          <div className="mt-1 text-[11px] text-slate-500">Milestones fully captured</div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-5 backdrop-blur-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">In-Flight Checkouts</div>
          <div className="mt-2 font-mono text-2xl font-bold text-cyan-400 flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            <span>{inProgressCount}</span>
          </div>
          <div className="mt-1 text-[11px] text-slate-500">Orders created or processing</div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <Filter className="h-3.5 w-3.5 text-cyan-400" />
            <span>Filters:</span>
          </div>

          <select
            value={providerFilter}
            onChange={(e) => setProviderFilter(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs font-semibold text-slate-200 focus:border-cyan-500 focus:outline-none"
          >
            <option value="all">All Providers</option>
            <option value="paypal">PayPal Sandbox</option>
            <option value="mock">Simulated (Mock)</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs font-semibold text-slate-200 focus:border-cyan-500 focus:outline-none"
          >
            <option value="all">All Statuses</option>
            <option value="completed">Completed</option>
            <option value="order_created">Order Created</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        <button
          onClick={loadPayments}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Error State */}
      {errorMessage && (
        <div className="rounded-xl border border-rose-500/40 bg-rose-950/50 p-4 text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-400" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Table Content */}
      {isLoading ? (
        <div className="py-20 flex flex-col items-center justify-center text-slate-400 space-y-3 font-mono text-xs">
          <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
          <span>Loading payment audit log...</span>
        </div>
      ) : (
        <PaymentHistoryTable payments={payments} />
      )}
    </div>
  );
};
