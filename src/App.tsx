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
    latency_ms: number;
    error_rate_pct: number;
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
  identifiedFactors: string[];
  mitigationSuggestions: {
    action: string;
    description: string;
  }[];
};

/* ---------- App ---------- */

export default function App() {
  /* ---------- Core system state ---------- */
  const [topology, setTopology] = useState<Topology | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [systemMode, setSystemMode] = useState<SystemMode>("healthy");

  /* ---------- AI explanation ---------- */
  const [explanation, setExplanation] = useState<Explanation | null>(null);

  /* ---------- UI state ---------- */
  const [loading, setLoading] = useState(false);

  /* ---------- Scenario & gating ---------- */
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [hasInjectedFailure, setHasInjectedFailure] = useState(false);
  const [hasRunSimulation, setHasRunSimulation] = useState(false);

  /* =========================================================
     API CALLS
     ========================================================= */

  /**
   * Run simulation
   * - populates topology + metrics
   * - clears old AI explanation
   */
  async function runSimulation() {
    try {
      setLoading(true);
      setExplanation(null);

      const res = await fetch("http://127.0.0.1:8000/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario: activeScenario,
        }),
      });

      if (!res.ok) throw new Error("Simulation failed");

      const data = await res.json();

      setTopology(data.topology);
      setMetrics(data.metrics);
      setSystemMode(data.system_mode);

      setHasRunSimulation(true);
    } catch (err) {
      console.error("Run simulation error:", err);
    } finally {
      setLoading(false);
    }
  }

  /**
   * Inject failure
   * - selects scenario only
   */
  function injectFailure(scenario: string) {
    setActiveScenario(scenario);
    setHasInjectedFailure(true);
    setExplanation(null);
  }

  /**
   * Run AI explanation
   * - HARD gated
   * - normalizes backend response
   */
  async function runExplanation() {
    if (!activeScenario || !hasInjectedFailure || !hasRunSimulation) {
      console.warn(
        "Explain blocked: select scenario, inject failure, then run simulation."
      );
      return;
    }

    try {
      setLoading(true);

      const res = await fetch("http://127.0.0.1:8000/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: activeScenario }),
      });

      if (!res.ok) throw new Error("Explain failed");

      const data = await res.json();

      // 🔑 Normalize backend → frontend shape
      setExplanation({
        text: data.text ?? [],
        identifiedFactors: data.identified_factors ?? [],
        mitigationSuggestions: data.mitigation_suggestions ?? [],
      });
    } catch (err) {
      console.error("Explain error:", err);
    } finally {
      setLoading(false);
    }
  }

  /* =========================================================
     RENDER
     ========================================================= */

  const canExplain =
    Boolean(activeScenario && hasInjectedFailure && hasRunSimulation && topology);

  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav
        onRunSimulation={runSimulation}
        loading={loading}
        systemMode={systemMode}
      />

      <main className="max-w-[1600px] mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* ---------- System Topology ---------- */}
          <div className="col-span-3">
            <SystemTopology
              topology={topology}
              onInjectFailure={injectFailure}
              onExplain={runExplanation}
              loading={loading}
              canExplain={canExplain}
            />
          </div>

          {/* ---------- Metrics ---------- */}
          <div className="col-span-5">
            <MetricsPanel
              metrics={metrics}
              systemMode={systemMode}
              systemExplanation={explanation?.text?.[0]}
            />
          </div>

          {/* ---------- AI Explanation ---------- */}
          <div className="col-span-4">
            <ExplanationPanel
              explanation={explanation}
              loading={loading}
            />
          </div>
        </div>
      </main>
    </div>
  );
}