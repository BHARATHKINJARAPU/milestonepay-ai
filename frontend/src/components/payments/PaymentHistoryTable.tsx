import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, DollarSign, History } from 'lucide-react';
import { Payment } from '../../types/payment';
import { PaymentStatusBadge } from './PaymentStatusBadge';

interface PaymentHistoryTableProps {
  payments: Payment[];
}

export const PaymentHistoryTable: React.FC<PaymentHistoryTableProps> = ({ payments }) => {
  if (payments.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/30 p-12 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800/80 text-slate-400">
          <History className="h-6 w-6" />
        </div>
        <h3 className="mt-4 text-sm font-semibold text-white">No Payment Records Yet</h3>
        <p className="mt-1 text-xs text-slate-400 max-w-sm mx-auto">
          Completed or initiated milestone release transactions will appear here with complete audit trail details.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/40 backdrop-blur-sm">
      <table className="w-full text-left text-xs">
        <thead className="border-b border-slate-800 bg-slate-950/60 font-semibold uppercase tracking-wider text-slate-400">
          <tr>
            <th className="px-5 py-3.5">Date & Time</th>
            <th className="px-5 py-3.5">Milestone / Scope</th>
            <th className="px-5 py-3.5">Amount</th>
            <th className="px-5 py-3.5">Provider</th>
            <th className="px-5 py-3.5">Status</th>
            <th className="px-5 py-3.5">Capture Reference</th>
            <th className="px-5 py-3.5 text-right">Receipt</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/80">
          {payments.map((payment) => {
            const formattedAmount = Number(payment.amount).toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            });

            return (
              <tr
                key={payment.id}
                className="hover:bg-slate-800/30 transition-colors"
              >
                <td className="px-5 py-4 font-mono text-slate-400 whitespace-nowrap">
                  {new Date(payment.created_at).toLocaleDateString()}
                  <span className="block text-[11px] text-slate-500">
                    {new Date(payment.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </td>

                <td className="px-5 py-4 max-w-xs">
                  <div className="font-semibold text-white truncate">
                    {payment.milestone?.title || (payment.provider_metadata?.milestone_title as string) || 'Milestone Deliverable'}
                  </div>
                  <div className="text-[11px] text-slate-400 truncate">
                    {payment.project?.title || (payment.provider_metadata?.project_title as string) || 'Project'}
                  </div>
                </td>

                <td className="px-5 py-4 whitespace-nowrap">
                  <div className="font-mono text-sm font-bold text-white flex items-center">
                    <DollarSign className="h-3.5 w-3.5 text-cyan-400" />
                    {formattedAmount} <span className="ml-1 text-[11px] text-slate-400">{payment.currency}</span>
                  </div>
                </td>

                <td className="px-5 py-4 whitespace-nowrap">
                  <span
                    className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider ${
                      payment.provider === 'paypal'
                        ? 'border-blue-500/40 bg-blue-950/60 text-blue-300'
                        : 'border-amber-500/40 bg-amber-950/60 text-amber-300'
                    }`}
                  >
                    {payment.provider === 'paypal' ? 'PayPal Sandbox' : 'Simulated (Mock)'}
                  </span>
                </td>

                <td className="px-5 py-4 whitespace-nowrap">
                  <PaymentStatusBadge status={payment.status} />
                </td>

                <td className="px-5 py-4 font-mono text-slate-400 whitespace-nowrap">
                  {payment.provider_capture_id ? (
                    <span className="text-emerald-400 font-semibold">{payment.provider_capture_id}</span>
                  ) : payment.provider_order_id ? (
                    <span className="text-cyan-400">{payment.provider_order_id}</span>
                  ) : (
                    <span className="text-slate-500">Pending</span>
                  )}
                </td>

                <td className="px-5 py-4 text-right whitespace-nowrap">
                  <Link
                    to={`/payments/${payment.id}/result`}
                    className="inline-flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-800 px-2.5 py-1 text-slate-300 hover:text-white hover:border-slate-600 transition-colors"
                  >
                    <span>View</span>
                    <ArrowUpRight className="h-3 w-3" />
                  </Link>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
