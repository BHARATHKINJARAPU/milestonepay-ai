import React from 'react';
import { TrendingUp } from 'lucide-react';
import { PaymentTrendsItem } from '../../types/analytics';

interface PaymentTrendChartProps {
  trends: PaymentTrendsItem[];
}

export const PaymentTrendChart: React.FC<PaymentTrendChartProps> = ({ trends }) => {
  if (!trends || trends.length === 0) {
    return (
      <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-emerald-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-white font-mono">
              Settlement Trends
            </h3>
          </div>
        </div>
        <div className="py-12 text-center text-xs text-slate-500">
          No settled payments recorded yet. Completed milestone checkouts will populate this chart.
        </div>
      </div>
    );
  }

  // Calculate scales
  const maxAmount = Math.max(
    ...trends.map((t) => Math.max(t.completed_paypal_amount, t.completed_mock_amount)),
    100
  );

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-emerald-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-white font-mono">
            Settlement Trends
          </h3>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-blue-500" />
            <span className="text-slate-400">PayPal Sandbox</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-amber-500" />
            <span className="text-slate-400">Simulated Mock</span>
          </div>
        </div>
      </div>

      {/* SVG Bar Chart Visualization */}
      <div className="h-44 w-full flex items-end gap-2 sm:gap-4 pt-6 pb-2 px-2">
        {trends.map((item, idx) => {
          const ppHeight = Math.max(6, Math.round((item.completed_paypal_amount / maxAmount) * 100));
          const mockHeight = Math.max(6, Math.round((item.completed_mock_amount / maxAmount) * 100));

          return (
            <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group">
              {/* Amounts tooltip on hover */}
              <div className="opacity-0 group-hover:opacity-100 transition-opacity bg-slate-950 border border-slate-800 rounded px-1.5 py-0.5 text-[9px] font-mono text-white whitespace-nowrap shadow-md pointer-events-none mb-1">
                ${(item.completed_paypal_amount + item.completed_mock_amount).toFixed(2)}
              </div>

              {/* Stacked or side-by-side bars */}
              <div className="w-full flex items-end justify-center gap-1 h-32">
                {item.completed_paypal_amount > 0 && (
                  <div
                    style={{ height: `${ppHeight}%` }}
                    className="w-1/2 max-w-5 bg-gradient-to-t from-blue-600 to-cyan-400 rounded-t-md transition-all group-hover:brightness-125"
                    title={`PayPal: $${item.completed_paypal_amount.toFixed(2)}`}
                  />
                )}
                {item.completed_mock_amount > 0 && (
                  <div
                    style={{ height: `${mockHeight}%` }}
                    className="w-1/2 max-w-5 bg-gradient-to-t from-amber-600 to-amber-400 rounded-t-md transition-all group-hover:brightness-125"
                    title={`Mock: $${item.completed_mock_amount.toFixed(2)}`}
                  />
                )}
              </div>

              {/* Date label */}
              <span className="text-[10px] font-mono text-slate-500 truncate max-w-16">
                {item.date.slice(5)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

