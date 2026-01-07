import { useState } from "react";
import { ArrowDown, AlertTriangle } from "lucide-react";

/* ---------- Types ---------- */

type SystemMode = "healthy" | "degraded" | "unhealthy";

interface Service {
  id: string;
  name: string;
  status: SystemMode;
  latency_ms: number;
  error_rate_pct: number;
}

interface Dependency {
  source: string;
  target: string;
}

interface Topology {
  services: Service[];
  dependencies: Dependency[];
}

interface SystemTopologyProps {
  topology: Topology | null;
  onInjectFailure: (scenario: string) => void;
  onExplain: () => void;
  loading: boolean;
  canExplain: boolean;
}

/* ---------- Scenarios (FIXED) ---------- */

const SCENARIOS = [
  {
    label: "Database Latency Spike",
    value: "database_latency_spike",
  },
  {
    label: "External Dependency Degradation",
    value: "external_dependency_degradation",
  },
  {
    label: "Retry Amplification",
    value: "retry_amplification",
  },
];

/* ---------- Helpers ---------- */

function statusColor(status: SystemMode) {
  switch (status) {
    case "healthy":
      return "bg-green-500";
    case "degraded":
      return "bg-yellow-500";
    case "unhealthy":
      return "bg-red-500";
    default:
      return "bg-gray-400";
  }
}

/* ---------- Component ---------- */

export function SystemTopology({
  topology,
  onInjectFailure,
  onExplain,
  loading,
  canExplain,
}: SystemTopologyProps) {
  // IMPORTANT: state now stores ENUM VALUE, not label
  const [selectedScenario, setSelectedScenario] = useState(
    SCENARIOS[0].value
  );

  function handleInjectFailure() {
    // Sends enum-safe value to App.tsx → backend
    onInjectFailure(selectedScenario);
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      <h2 className="text-gray-900 mb-4">System Overview</h2>

      {/* ---------- Status Legend ---------- */}
      <div className="mb-4 pb-4 border-b border-gray-200">
        <div className="flex items-center gap-4 text-xs text-gray-600">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span>Healthy</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-yellow-500" />
            <span>Degraded</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <span>Unhealthy</span>
          </div>
        </div>
      </div>

      {/* ---------- Topology ---------- */}
      {!topology ? (
        <p className="text-sm text-gray-500">
          Run a simulation to view system topology
        </p>
      ) : (
        <div className="mb-6 space-y-3">
          {topology.services.map((service, idx) => (
            <div key={service.id}>
              <div className="p-3 bg-gray-50 rounded border border-gray-200">
                <div className="flex items-center gap-3 mb-1">
                  <div
                    className={`w-2 h-2 rounded-full ${statusColor(
                      service.status
                    )}`}
                  />
                  <span className="text-sm font-medium text-gray-900">
                    {service.name}
                  </span>
                </div>

                <div className="ml-5 text-xs text-gray-600 space-y-0.5">
                  <div>Latency: {Math.round(service.latency_ms)} ms</div>
                  <div>
                    Errors: {(service.error_rate_pct * 100).toFixed(2)} %
                  </div>
                </div>
              </div>

              {idx < topology.services.length - 1 && (
                <div className="flex justify-center py-1">
                  <ArrowDown className="w-4 h-4 text-gray-400" />
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ---------- Scenario Controls ---------- */}
      <div className="space-y-3">
        <div>
          <label className="block text-sm text-gray-700 mb-2">
            Failure Scenario
          </label>

          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm"
          >
            {SCENARIOS.map((scenario) => (
              <option key={scenario.value} value={scenario.value}>
                {scenario.label}
              </option>
            ))}
          </select>
        </div>

        {/* Inject Failure */}
        <button
          disabled={loading}
          onClick={handleInjectFailure}
          className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-orange-400 text-white px-4 py-2 rounded-md flex items-center justify-center gap-2"
        >
          <AlertTriangle className="w-4 h-4" />
          Inject Failure
        </button>

        {/* Explain Failure */}
        <button
          disabled={loading || !canExplain}
          onClick={onExplain}
          className="w-full bg-gray-900 hover:bg-gray-800 disabled:bg-gray-400 text-white px-4 py-2 rounded-md"
        >
          Explain Failure
        </button>

        {!canExplain && (
          <p className="text-xs text-gray-500 text-center">
            Select a scenario, inject failure, and run a simulation first
          </p>
        )}
      </div>
    </div>
  );
}
