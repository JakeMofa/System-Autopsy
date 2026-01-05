//App.tsx
import { TopNav } from './components/TopNav';
import { SystemTopology } from './components/SystemTopology';
import { MetricsPanel } from './components/MetricsPanel';
import { ExplanationPanel } from './components/ExplanationPanel';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav />
      
      <main className="max-w-[1600px] mx-auto px-6 py-6">
        {/* 3-column grid layout */}
        <div className="grid grid-cols-12 gap-6">
          {/* Left column - System Topology */}
          <div className="col-span-3">
            <SystemTopology />
          </div>
          
          {/* Center column - Metrics */}
          <div className="col-span-5">
            <MetricsPanel />
          </div>
          
          {/* Right column - AI Explanation */}
          <div className="col-span-4">
            <ExplanationPanel />
          </div>
        </div>
      </main>
    </div>
  );
}