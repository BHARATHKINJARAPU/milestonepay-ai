import React from 'react';
import { MessageSquareText, Sparkles, CreditCard, CheckCircle } from 'lucide-react';

export const HowItWorks: React.FC = () => {
  const stages = [
    {
      step: '01',
      title: 'Describe Your Project',
      icon: MessageSquareText,
      accent: 'from-blue-600 to-cyan-500',
      badgeColor: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
      description:
        'Input rough briefs, informal client notes, or vague requirements without worrying about formatting or missing details.',
      details: [
        'Supports unstructured client messages and rough scopes',
        'Captures business goals, timelines, and budgets',
        'Eliminates endless email chains before kickoff',
      ],
    },
    {
      step: '02',
      title: 'Generate Clear Milestones',
      icon: Sparkles,
      accent: 'from-indigo-600 to-violet-500',
      badgeColor: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
      description:
        'Intelligent AI decomposes the scope into bite-sized milestones with unambiguous acceptance criteria and budget allocations.',
      details: [
        'Automated breakdown into distinct deliverable phases',
        'Explicit acceptance criteria both parties agree upon',
        'Realistic timeline and milestone pricing estimates',
      ],
    },
    {
      step: '03',
      title: 'Deliver, Review & Get Paid',
      icon: CreditCard,
      accent: 'from-violet-600 to-emerald-500',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
      description:
        'Submit deliverables, receive AI-assisted verification feedback, and get funds released directly upon client sign-off.',
      details: [
        'AI assistance highlights requirement fulfillment',
        'Client retains authoritative final review and approval',
        'Frictionless milestone release via PayPal checkout',
      ],
    },
  ];

  return (
    <section id="how-it-works" className="py-24 bg-slate-950/60 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
            <span>The 3-Step Process</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
            How MilestonePay AI Works
          </h2>
          <p className="text-base sm:text-lg text-slate-400">
            From chaotic project scopes to predictable payouts. A streamlined framework designed to protect both clients and freelancers.
          </p>
        </div>

        {/* 3-Stage Process Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {stages.map((stage) => {
            const Icon = stage.icon;
            return (
              <div
                key={stage.step}
                className="relative rounded-2xl p-7 bg-slate-900/60 border border-slate-800 hover:border-slate-700/80 transition-all duration-300 flex flex-col justify-between group hover:shadow-xl hover:shadow-blue-900/10"
              >
                {/* Step indicator watermark & Icon header */}
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stage.accent} p-0.5 shadow-lg`}>
                      <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                    </div>
                    <span className="font-mono text-2xl font-black text-slate-700 group-hover:text-slate-500 transition-colors">
                      {stage.step}
                    </span>
                  </div>

                  {/* Stage Title */}
                  <h3 className="text-xl font-bold text-white mb-3">
                    {stage.title}
                  </h3>

                  {/* Description */}
                  <p className="text-sm text-slate-300 leading-relaxed mb-6">
                    {stage.description}
                  </p>
                </div>

                {/* Bulleted details */}
                <div className="pt-4 border-t border-slate-800/80 space-y-2.5">
                  {stage.details.map((detail, dIdx) => (
                    <div key={dIdx} className="flex items-start gap-2.5 text-xs text-slate-400">
                      <CheckCircle className="w-3.5 h-3.5 text-blue-400 mt-0.5 shrink-0" />
                      <span>{detail}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
