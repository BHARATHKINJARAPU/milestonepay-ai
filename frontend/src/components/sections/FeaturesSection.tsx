import React from 'react';
import { 
  Wand2, 
  FileCheck2, 
  Users2, 
  GitPullRequest, 
  WalletCards, 
  LineChart,
  CalendarDays
} from 'lucide-react';

export const FeaturesSection: React.FC = () => {
  const features = [
    {
      title: 'AI Milestone Generator',
      icon: Wand2,
      badge: 'Planned Capability',
      description:
        'Converts messy project descriptions into structured milestone breakdown with deliverables, deadlines, and budget allocations using Gemini AI.',
      techNote: 'Target: Phase 2 (AI Engine)',
    },
    {
      title: 'Smart Deliverable Evaluation',
      icon: FileCheck2,
      badge: 'Planned Capability',
      description:
        'Analyzes submitted files, code, or documentation against the previously agreed acceptance criteria to flag gaps before client review.',
      techNote: 'Target: Phase 2 (AI Reviewer)',
    },
    {
      title: 'Client & Freelancer Collaboration',
      icon: Users2,
      badge: 'Planned Capability',
      description:
        'Shared agreement workspace where both parties review, suggest edits, and formally agree on milestone boundaries prior to starting work.',
      techNote: 'Target: Phase 3 (Collaboration)',
    },
    {
      title: 'Milestone Approval Workflow',
      icon: GitPullRequest,
      badge: 'Planned Capability',
      description:
        'Multi-stage verification gate ensuring the client retains final sign-off authority while preventing arbitrary scope expansion.',
      techNote: 'Target: Phase 3 (Workflow Engine)',
    },
    {
      title: 'PayPal Payment Integration',
      icon: WalletCards,
      badge: 'Planned Capability',
      description:
        'Direct PayPal Sandbox checkout integration for secure milestone payments and verified client approvals upon delivery.',
      techNote: 'Target: Phase 4 (Fintech Bridge)',
    },
    {
      title: 'Project Progress Tracking',
      icon: LineChart,
      badge: 'Planned Capability',
      description:
        'Real-time timeline and budget tracking dashboard providing full visibility into completed milestones and pending payouts.',
      techNote: 'Target: Phase 4 (Analytics Dashboard)',
    },
  ];

  return (
    <section id="features" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300">
            <CalendarDays className="w-3.5 h-3.5 text-blue-400" />
            <span>Product Roadmap & Architecture</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
            Planned Product Capabilities
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            MilestonePay AI is being built in structured phases. Here is the upcoming feature architecture being built upon today's Day 1 foundation.
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div
                key={idx}
                className="rounded-2xl p-6 bg-slate-900/50 border border-slate-800 hover:border-blue-500/30 transition-all duration-200 flex flex-col justify-between group hover:bg-slate-900/80"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-10 h-10 rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-center group-hover:border-blue-500/40 group-hover:bg-blue-500/10 transition-colors">
                      <Icon className="w-5 h-5 text-blue-400 group-hover:text-blue-300" />
                    </div>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {feature.badge}
                    </span>
                  </div>

                  <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-blue-200 transition-colors">
                    {feature.title}
                  </h3>

                  <p className="text-sm text-slate-400 leading-relaxed">
                    {feature.description}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono text-slate-500">
                  <span>Architecture</span>
                  <span className="text-blue-400/90">{feature.techNote}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
