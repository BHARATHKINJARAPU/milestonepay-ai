import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle2, Clock, CreditCard, FileText } from 'lucide-react';
import { ReviewCenterItem } from '../../types/analytics';

interface ReviewCenterListProps {
  items: ReviewCenterItem[];
}

export const ReviewCenterList: React.FC<ReviewCenterListProps> = ({ items }) => {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-amber-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-white font-mono">
            Milestone Review Center
          </h3>
          <span className="text-xs text-slate-500 font-mono">({items.length} pending actions)</span>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="py-8 text-center text-xs text-slate-500">
          No items currently require your review. All submitted work is up to date!
        </div>
      ) : (
        <div className="space-y-2.5">
          {items.map((item, idx) => {
            const isPayment = item.item_type === 'pending_payment';
            const isPlan = item.item_type === 'plan_review';

            return (
              <div
                key={idx}
                className={`flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 rounded-2xl border transition-all ${
                  isPayment
                    ? 'border-emerald-500/30 bg-emerald-950/20 hover:border-emerald-500/50'
                    : isPlan
                    ? 'border-violet-500/30 bg-violet-950/20 hover:border-violet-500/50'
                    : 'border-blue-500/30 bg-blue-950/20 hover:border-blue-500/50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl border mt-0.5 ${
                      isPayment
                        ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400'
                        : isPlan
                        ? 'bg-violet-500/20 border-violet-500/40 text-violet-400'
                        : 'bg-blue-500/20 border-blue-500/40 text-blue-400'
                    }`}
                  >
                    {isPayment ? (
                      <CreditCard className="h-4 w-4" />
                    ) : isPlan ? (
                      <FileText className="h-4 w-4" />
                    ) : (
                      <CheckCircle2 className="h-4 w-4" />
                    )}
                  </div>

                  <div>
                    <span className="text-[10px] font-mono font-bold uppercase text-slate-400">
                      {item.project_title}
                    </span>
                    <h4 className="text-xs font-bold text-white mt-0.5">{item.title}</h4>
                    <p className="text-[11px] text-slate-300 mt-0.5">{item.subtitle}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 w-full sm:w-auto justify-end pt-2 sm:pt-0">
                  {item.amount && (
                    <span className="font-mono text-xs font-bold text-white">
                      {item.currency} ${item.amount.toFixed(2)}
                    </span>
                  )}
                  <Link
                    to={item.action_url}
                    className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold text-white shadow-sm transition-all ${
                      isPayment
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500'
                        : 'bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500'
                    }`}
                  >
                    <span>{isPayment ? 'Release Funds' : 'Review Now'}</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

