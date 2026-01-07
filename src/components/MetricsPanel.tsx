// src/components/MetricsPanel.tsx
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

/* ---------- Types ---------- */

interface MetricPoint {
  time: number;
  value: number;
}

/**
 * Metrics coming from backend
 * All fields OPTIONAL to prevent render crashes
 */
interface Metrics {
  latency_ms?: MetricPoint[];
  error_rate_pct?: MetricPoint[];
  request_volume?: MetricPoint[];
  queue_depth?: MetricPoint[];
}

interface MetricChartProps {
  title: string;
  data: Array<{ time: string; value: number }>;
  color: string;
  unit?: string;
}

/* ---------- Chart ---------- */

function MetricChart({ title, data, color, unit = "" }: MetricChartProps) {
  return (
    <div className="mb-6">
      <h3 className="text-sm text-gray-700 mb-3">{title}</h3>

      <ResponsiveContainer width="100%" height={140}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />

          <XAxis
            dataKey="time"
            tick={{ fontSize: 11, fill: "#6b7280" }}
            stroke="#d1d5db"
          />

          <YAxis
            tick={{ fontSize: 11, fill: "#6b7280" }}
            stroke="#d1d5db"
            tickFormatter={(value) => `${Math.round(value)}${unit}`}
          />

          <Tooltip
            contentStyle={{
              fontSize: "12px",
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "6px",
            }}
            formatter={(value: number) => [
              `${Math.round(value)}${unit}`,
              title,
            ]}
          />

          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

/* ---------- Panel ---------- */

export function MetricsPanel({
  metrics,
  systemMode,
  aiSystemStateText, // App.tsx
}: {
  metrics: Metrics | null;
  systemMode: string;
  aiSystemStateText?: string | null;
}) {
  // Empty state before simulation
  if (!metrics) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h2 className="text-gray-900 mb-5">Operational Metrics</h2>
        <p className="text-sm text-gray-500">
          Run a simulation to view metrics
        </p>
      </div>
    );
  }

  /* ---------- Defensive mapping ---------- */

  const latencyData =
    metrics.latency_ms?.map((m) => ({
      time: `${m.time}m`,
      value: m.value,
    })) ?? [];

  const errorRateData =
    metrics.error_rate_pct?.map((m) => ({
      time: `${m.time}m`,
      value: m.value * 100,
    })) ?? [];

  const requestVolumeData =
    metrics.request_volume?.map((m) => ({
      time: `${m.time}m`,
      value: m.value,
    })) ?? [];

  const queueDepthData =
    metrics.queue_depth?.map((m) => ({
      time: `${m.time}m`,
      value: m.value,
    })) ?? [];

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      <h2 className="text-gray-900 mb-5">Operational Metrics</h2>

      <MetricChart
        title="P95 Latency (ms)"
        data={latencyData}
        color="#3b82f6"
        unit="ms"
      />

      <MetricChart
        title="Error Rate (%)"
        data={errorRateData}
        color="#ef4444"
        unit="%"
      />

      <MetricChart
        title="Request Volume (RPS)"
        data={requestVolumeData}
        color="#10b981"
      />

      <MetricChart
        title="Queue Depth"
        data={queueDepthData}
        color="#f59e0b"
      />

      {/* ---------- System State ---------- */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-sm text-gray-700 mb-3">System State</h3>

        <div className="bg-amber-50 border border-amber-200 rounded-md p-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-amber-500" />
            <span className="text-sm text-gray-900">
              System Mode: {systemMode}
            </span>
          </div>

          <p className="text-sm text-gray-600 leading-relaxed">
            {aiSystemStateText ??
              "System behavior reflects the current simulation state and dependency-driven degradation across services."}
          </p>
        </div>
      </div>
    </div>
  );
}
