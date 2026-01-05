//TopNav.tsx
import { Play, Loader2 } from 'lucide-react';
import { useState } from 'react';

export function TopNav() {
  const [isRunning, setIsRunning] = useState(false);
  
  const handleRunSimulation = async () => {
    setIsRunning(true);
    // Simulate API call to /simulate endpoint
    // This would reset and run a new simulation from clean state
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsRunning(false);
  };
  
  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="max-w-[1600px] mx-auto flex items-center justify-between">
        <div>
          <h1 className="text-gray-900">System Autopsy</h1>
          <p className="text-gray-500 text-sm mt-0.5">Failure Simulation & Explanation</p>
        </div>
        
        <button 
          onClick={handleRunSimulation}
          disabled={isRunning}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-md flex items-center gap-2 transition-colors"
        >
          {isRunning ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Running Simulation...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Run Simulation
            </>
          )}
        </button>
      </div>
    </nav>
  );
}