/* src/App.tsx */
import { useState } from "react";

import { TopNav } from "./components/TopNav";
import { SystemTopology } from "./components/SystemTopology";
import { MetricsPanel } from "./components/MetricsPanel";
import { ExplanationPanel } from "./components/ExplanationPanel";

/* ---------- Types ---------- */

type SystemMode = "healthy" | "degraded" | "unhealthy";

type Topology = {
  services: {
    id: string;
    name: string;
    status: SystemMode;
  }[];
  dependencies: {
    source: string;
    target: string;
  }[];
};

type MetricPoint = {
  time: number;
  value: number;
};

type Metrics = {
  latency_ms: MetricPoint[];
  error_rate_pct: MetricPoint[];
  request_volume: MetricPoint[];
  queue_depth: MetricPoint[];
};

type Explanation = {
  text: string[];
  identified_factors: string[];
  mitigation_suggestions: {
    action: string;
    description: string;
  }[];
};

/* ---------- App ---------- */

export default function App() {
  const [topology, setTopology] = useState<Topology | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [systemMode, setSystemMode] = useState<SystemMode>("healthy");

  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [loading, setLoading] = useState(false);

  // Selected failure scenario (set by Inject Failure)
  const [activeScenario, setActiveScenario] = useState<string | null>(null);

  /* ---------- API calls ---------- */

  // Run simulation (uses selected scenario)
  async function runSimulation() {
    try {
      setLoading(true);
      setExplanation(null);

      const res = await fetch("http://127.0.0.1:8000/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario: activeScenario, // 
        }),
      });

      if (!res.ok) throw new Error("Simulation failed");

      const data = await res.json();

      setTopology(data.topology);
      setMetrics(data.metrics);
      setSystemMode(data.system_mode);
    } catch (err) {
      console.error("Run simulation error:", err);
    } finally {
      setLoading(false);
    }
  }

  // Inject failure = SELECT scenario only
  function injectFailure(scenario: string) {
    console.log("Active scenario set to:", scenario);
    setActiveScenario(scenario);
    setExplanation(null);
  }

  // Run AI explanation (uses selected scenario)
  async function runExplanation() {
    if (!activeScenario) return;

    try {
      setLoading(true);

      const res = await fetch("http://127.0.0.1:8000/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: activeScenario }),
      });

      if (!res.ok) throw new Error("Explain failed");

      const data = await res.json();
      setExplanation(data);
    } catch (err) {
      console.error("Explain error:", err);
    } finally {
      setLoading(false);
    }
  }

  /* ---------- Render ---------- */

  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav
        onRunSimulation={runSimulation}
        loading={loading}
        systemMode={systemMode}
      />

      <main className="max-w-[1600px] mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* System Topology */}
          <div className="col-span-3">
            <SystemTopology
              topology={topology}
              onInjectFailure={injectFailure}
              onExplain={runExplanation}
              loading={loading}
            />
          </div>

          {/* Metrics */}
          <div className="col-span-5">
            <MetricsPanel metrics={metrics} systemMode={systemMode} />
          </div>

          {/* AI Explanation */}
          <div className="col-span-4">
            <ExplanationPanel
              explanation={explanation}
              systemMode={systemMode}
              loading={loading}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
