import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Navbar } from './components/layout/Navbar';
import { HeroSection } from './components/sections/HeroSection';
import { HowItWorks } from './components/sections/HowItWorks';
import { FeaturesSection } from './components/sections/FeaturesSection';
import { ConnectionStatus } from './components/status/ConnectionStatus';
import { Footer } from './components/layout/Footer';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white bg-grid-pattern">
        {/* Navigation Bar */}
        <Navbar />

        {/* Main Content */}
        <main className="flex-1">
          {/* Hero Section */}
          <HeroSection />

          {/* How It Works (3-Stage Workflow) */}
          <HowItWorks />

          {/* Features Section (6 Planned Capabilities) */}
          <FeaturesSection />

          {/* Live System Diagnostics (Real FastAPI & PostgreSQL checks) */}
          <ConnectionStatus />
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </BrowserRouter>
  );
};

export default App;
