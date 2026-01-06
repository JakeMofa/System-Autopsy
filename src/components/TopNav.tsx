// TopNav.tsx
import { Play, Loader2 } from "lucide-react";

interface TopNavProps {
  onRunSimulation: () => Promise<void>;
  loading: boolean;
}

export function TopNav({ onRunSimulation, loading }: TopNavProps) {
  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="max-w-[1600px] mx-auto flex items-center justify-between">
        <div>
          <h1 className="text-gray-900">System Autopsy</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Failure Simulation & Explanation
          </p>
        </div>

        <button
          onClick={onRunSimulation}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white px-4 py-2 rounded-md flex items-center gap-2 transition-colors"
        >
          {loading ? (
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
