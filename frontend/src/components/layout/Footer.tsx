import React from 'react';
import { Layers } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-950 border-t border-slate-900 py-12 text-slate-400 text-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 pb-10 border-b border-slate-900">
          {/* Brand info */}
          <div className="md:col-span-5 space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-violet-600 p-0.5">
                <div className="w-full h-full bg-slate-950 rounded-[6px] flex items-center justify-center">
                  <Layers className="w-4 h-4 text-blue-400" />
                </div>
              </div>
              <span className="text-base font-bold text-white tracking-tight">MilestonePay AI</span>
            </div>
            <p className="text-xs text-slate-400 max-w-sm leading-relaxed">
              Work Smarter. Deliver Transparently. Get Paid Confidently. AI-powered freelance milestone and payment management platform.
            </p>
            <p className="text-[11px] text-slate-400 font-mono">
              Day 1 Technical Foundation • React + FastAPI + PostgreSQL
            </p>
          </div>

          {/* Navigation anchors */}
          <div className="md:col-span-3 space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300 font-mono">Navigation</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="#" className="hover:text-white transition-colors">Home</a>
              </li>
              <li>
                <a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a>
              </li>
              <li>
                <a href="#features" className="hover:text-white transition-colors">Planned Features</a>
              </li>
              <li>
                <a href="#system-status" className="hover:text-white transition-colors">System Diagnostics</a>
              </li>
            </ul>
          </div>

          {/* Project & Tech Architecture */}
          <div className="md:col-span-4 space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300 font-mono">Architecture</h4>
            <ul className="space-y-1.5 text-xs text-slate-400">
              <li><span className="text-slate-300">Frontend:</span> React 19, TypeScript, Tailwind CSS v4, Vite</li>
              <li><span className="text-slate-300">Backend:</span> Python 3.12+, FastAPI, SQLAlchemy 2.x</li>
              <li><span className="text-slate-300">Database:</span> PostgreSQL 16 (Psycopg 3)</li>
              <li><span className="text-slate-300">Future Integrations:</span> Gemini AI & PayPal Sandbox</li>
            </ul>
          </div>
        </div>

        {/* Bottom Attribution */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <p>© {new Date().getFullYear()} MilestonePay AI. Built for the Hackathon.</p>
          <div className="flex items-center gap-6">
            <span className="font-mono text-[11px] text-blue-400">Day 1 Foundation Setup Complete</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
