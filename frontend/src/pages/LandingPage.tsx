import React from 'react';
import { Navbar } from '../components/layout/Navbar';
import { HeroSection } from '../components/sections/HeroSection';
import { HowItWorks } from '../components/sections/HowItWorks';
import { FeaturesSection } from '../components/sections/FeaturesSection';
import { ConnectionStatus } from '../components/status/ConnectionStatus';
import { Footer } from '../components/layout/Footer';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white bg-grid-pattern">
      <Navbar />
      <main className="flex-1">
        <HeroSection />
        <HowItWorks />
        <FeaturesSection />
        <ConnectionStatus />
      </main>
      <Footer />
    </div>
  );
};

