import React from 'react';
import { CheckCircle2, DollarSign, Layers, ShieldCheck, User } from 'lucide-react';
import { Milestone } from '../../types/milestone';
import { Project } from '../../types/project';
import { PaymentStatusBadge } from './PaymentStatusBadge';
import { PaymentStatus } from '../../types/payment';

interface PaymentSummaryProps {
  project: Project;
  milestone: Milestone;
  freelancerName?: string;
  paymentStatus?: PaymentStatus;
}

export const PaymentSummary: React.FC<PaymentSummaryProps> = ({
  project,
  milestone,
  freelancerName = 'Assigned Freelancer',
  paymentStatus,
}) => {
  const formattedAmount = Number(milestone.amount).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
            <Layers className="h-4 w-4" />
            <span>Payment Summary</span>
          </div>
          <h2 className="mt-2 text-xl font-bold text-white tracking-tight">
            {milestone.title}
          </h2>
          <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-slate-400">
            <span>Project: <strong className="text-slate-200">{project.title}</strong></span>
            <span>&bull;</span>
            <span className="font-mono">Milestone #{milestone.sequence_number}</span>
          </div>
        </div>

        {paymentStatus && (
          <PaymentStatusBadge status={paymentStatus} showProvider />
        )}
      </div>

      {/* Amount Display */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-cyan-500/20 bg-gradient-to-br from-cyan-950/40 to-slate-900/80 p-5">
          <div className="text-xs font-semibold uppercase tracking-wider text-cyan-400/80">
            Agreed Milestone Release
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <div className="flex items-center font-mono text-3xl font-extrabold text-white">
              <DollarSign className="h-6 w-6 text-cyan-400" />
              {formattedAmount}
            </div>
            <span className="font-mono text-sm font-semibold text-slate-400">{milestone.currency}</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400 flex items-center gap-1.5">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
            <span>Verified against agreed project contract ({milestone.budget_percentage}% of total budget)</span>
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-5 space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Recipient Freelancer
          </div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-800 text-cyan-400 border border-slate-700">
              <User className="h-5 w-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">{freelancerName}</div>
              <div className="text-[11px] text-slate-400">Assigned Deliverable Creator</div>
            </div>
          </div>
          <div className="pt-2 text-[11px] text-slate-500 border-t border-slate-800/80 flex items-center gap-1.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-cyan-400" />
            <span>Deliverables explicitly approved by client. Ready for checkout.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
