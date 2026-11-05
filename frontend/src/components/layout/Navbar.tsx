import React, { useState } from 'react';
import { Layers, Menu, X, ArrowRight } from 'lucide-react';

export const Navbar: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Logo & Brand */}
          <a href="#" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-violet-500 p-0.5 shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-all">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Layers className="w-5 h-5 text-blue-400 group-hover:scale-110 transition-transform" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                MilestonePay <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">AI</span>
              </span>
              <span className="text-[10px] text-slate-400 font-mono tracking-wider uppercase">Foundation • Day 1</span>
            </div>
          </a>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center gap-8">
            <a href="#" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
              Home
            </a>
            <a href="#how-it-works" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
              How It Works
            </a>
            <a href="#features" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
              Features
            </a>
            <a href="#system-status" className="text-sm font-medium text-slate-300 hover:text-white transition-colors flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Live Diagnostics
            </a>
          </div>

          {/* Visual Entry Points (Non-functional placeholders for Day 1) */}
          <div className="hidden md:flex items-center gap-3">
            <button
              type="button"
              className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white rounded-lg hover:bg-slate-800/60 transition-colors"
              title="Authentication will be enabled in subsequent project phases"
            >
              Log In
            </button>
            <button
              type="button"
              className="px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 rounded-lg shadow-md shadow-blue-600/25 transition-all flex items-center gap-2"
              title="Get Started will open project setup workflow"
            >
              Get Started
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Mobile menu trigger */}
          <div className="flex md:hidden items-center">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 focus:outline-none"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-800 bg-slate-950/95 backdrop-blur-xl px-4 pt-3 pb-6 space-y-3">
          <a
            href="#"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-200 hover:bg-slate-800"
          >
            Home
          </a>
          <a
            href="#how-it-works"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-200 hover:bg-slate-800"
          >
            How It Works
          </a>
          <a
            href="#features"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-200 hover:bg-slate-800"
          >
            Features
          </a>
          <a
            href="#system-status"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-emerald-400 hover:bg-slate-800"
          >
            System Status
          </a>
          <div className="pt-4 border-t border-slate-800 flex flex-col gap-2">
            <button
              type="button"
              className="w-full text-center px-4 py-2.5 rounded-lg border border-slate-700 text-sm font-medium text-slate-300"
            >
              Log In
            </button>
            <button
              type="button"
              className="w-full text-center px-4 py-2.5 rounded-lg bg-blue-600 text-sm font-semibold text-white shadow-lg shadow-blue-600/30"
            >
              Get Started
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};
