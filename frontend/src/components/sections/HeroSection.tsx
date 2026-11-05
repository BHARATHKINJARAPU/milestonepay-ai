import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight, CheckCircle2, Clock, FileCode, CheckCheck, Cpu, Shield } from 'lucide-react';

export const HeroSection: React.FC = () => {
  return (
    <section className="relative pt-32 pb-20 md:pt-40 md:pb-32 overflow-hidden">
      {/* Background radial gradient glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[450px] bg-gradient-to-tr from-blue-600/15 via-indigo-500/10 to-violet-600/15 blur-[120px] pointer-events-none -z-10" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          {/* Left Column: Headline and Call to Actions */}
          <div className="lg:col-span-7 space-y-8 text-center lg:text-left">
            {/* Tagline Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-medium text-blue-400">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Next-Gen Freelance Work & Escrow Assurance</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.12]">
              Turn Unclear Projects <br className="hidden sm:inline" />
              Into <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-violet-400">Clear Milestones.</span>
            </h1>

            {/* Supporting Description */}
            <p className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto lg:mx-0 leading-relaxed font-normal">
              Plan freelance projects, define deliverables, evaluate progress, and manage milestone payments with intelligent AI assistance.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
              <a
                href="#how-it-works"
                className="w-full sm:w-auto px-7 py-3.5 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 shadow-xl shadow-blue-600/25 transition-all flex items-center justify-center gap-2 text-base group"
              >
                <span>Explore How It Works</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </a>

              <Link
                to="/register"
                className="w-full sm:w-auto px-7 py-3.5 rounded-xl font-medium text-slate-200 bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 hover:border-slate-600 transition-all text-base text-center"
              >
                Get Started
              </Link>
            </div>

            {/* Trust highlights */}
            <div className="pt-6 border-t border-slate-800/80 flex flex-wrap items-center justify-center lg:justify-start gap-6 text-xs text-slate-400">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-blue-400" />
                <span>Transparent Acceptance Criteria</span>
              </div>
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-indigo-400" />
                <span>AI Requirement Structuring</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCheck className="w-4 h-4 text-emerald-400" />
                <span>Client Retains Approval Authority</span>
              </div>
            </div>
          </div>

          {/* Right Column: Interactive CSS Workflow Diagram (Realistic preview of AI Milestone decomposition) */}
          <div className="lg:col-span-5 relative">
            <div className="relative mx-auto max-w-md lg:max-w-none">
              {/* Outer decorative card */}
              <div className="relative rounded-2xl p-6 bg-slate-900/90 border border-slate-800 shadow-2xl backdrop-blur-xl space-y-5">
                {/* Header: Raw Input prompt simulation */}
                <div className="space-y-2 pb-4 border-b border-slate-800">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span className="font-mono text-blue-400 font-medium flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                      RAW CLIENT SCOPE
                    </span>
                    <span className="text-[11px] bg-slate-800 px-2 py-0.5 rounded text-slate-300">Unstructured</span>
                  </div>
                  <p className="text-xs text-slate-300 italic bg-slate-950/70 p-3 rounded-lg border border-slate-800/60 leading-relaxed font-mono">
                    "Build a client portal with secure authentication, milestone delivery uploads, and PayPal sandbox checkout."
                  </p>
                </div>

                {/* AI Processing node */}
                <div className="flex items-center justify-center gap-2 py-1 text-xs font-semibold text-indigo-300">
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent to-indigo-500/40"></div>
                  <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-950/60 border border-indigo-500/30">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    <span>AI MILESTONE ENGINE</span>
                  </div>
                  <div className="h-px flex-1 bg-gradient-to-l from-transparent to-indigo-500/40"></div>
                </div>

                {/* Structured Milestone Items Preview */}
                <div className="space-y-3">
                  {/* Milestone 1 */}
                  <div className="p-3.5 rounded-xl bg-slate-950/60 border border-emerald-500/30 flex items-start gap-3">
                    <div className="mt-0.5 p-1 rounded-lg bg-emerald-500/20 text-emerald-400">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-semibold text-white">Milestone 1: Auth & Database Foundation</h4>
                        <span className="text-[11px] font-mono text-emerald-400 font-medium">Ready</span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1 truncate">FastAPI + PostgreSQL Docker container + schema validation</p>
                      <div className="mt-2 flex items-center gap-3 text-[10px] text-slate-500 font-mono">
                        <span>Target: Day 1</span>
                        <span>•</span>
                        <span>Deliverable: Verified Health Checks</span>
                      </div>
                    </div>
                  </div>

                  {/* Milestone 2 */}
                  <div className="p-3.5 rounded-xl bg-slate-950/60 border border-blue-500/30 flex items-start gap-3">
                    <div className="mt-0.5 p-1 rounded-lg bg-blue-500/20 text-blue-400">
                      <Clock className="w-4 h-4 animate-spin" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-semibold text-white">Milestone 2: AI Requirement Decomposition</h4>
                        <span className="text-[11px] font-mono text-blue-400 font-medium">Planned</span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1 truncate">Gemini prompt chaining for acceptance criteria generation</p>
                      <div className="mt-2 flex items-center gap-3 text-[10px] text-slate-500 font-mono">
                        <span>Target: Day 2</span>
                        <span>•</span>
                        <span>Deliverable: Scoped Milestones</span>
                      </div>
                    </div>
                  </div>

                  {/* Milestone 3 */}
                  <div className="p-3.5 rounded-xl bg-slate-950/40 border border-slate-800 flex items-start gap-3 opacity-80">
                    <div className="mt-0.5 p-1 rounded-lg bg-slate-800 text-slate-400">
                      <FileCode className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-semibold text-slate-300">Milestone 3: Deliverable Review & Payout</h4>
                        <span className="text-[11px] font-mono text-slate-400">Scheduled</span>
                      </div>
                      <p className="text-[11px] text-slate-500 mt-1 truncate">Client approval gate & PayPal Sandbox release</p>
                      <div className="mt-2 flex items-center gap-3 text-[10px] text-slate-500 font-mono">
                        <span>Target: Day 3</span>
                        <span>•</span>
                        <span>Deliverable: Payment Flow</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Footer of the workflow card */}
                <div className="pt-2 flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/80">
                  <span className="flex items-center gap-1.5 font-mono">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    Workflow Blueprint
                  </span>
                  <span className="text-slate-400">Objective: Zero Ambiguity</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

