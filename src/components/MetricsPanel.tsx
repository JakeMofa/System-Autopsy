//MetricsPanel/tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Mock data - in production this would come from /simulate API response
// Generate realistic time-series data
const generateMetricData = (baseValue: number, variance: number, spike: boolean = false) => {
  const data = [];
  for (let i = 0; i < 30; i++) {
    const random = Math.random() * variance;
    const spikeValue = spike && i > 15 && i < 25 ? baseValue * 2 : 0;
    data.push({
      time: `${i}m`,
      value: Math.max(0, baseValue + random + spikeValue),
    });
  }
  return data;
};

const latencyData = generateMetricData(120, 40, true);
const errorRateData = generateMetricData(0.5, 0.3, true);
const requestVolumeData = generateMetricData(450, 100, false);
const queueDepthData = generateMetricData(25, 15, true);

interface MetricChartProps {
  title: string;
  data: Array<{ time: string; value: number }>;
  color: string;
  unit?: string;
}

function MetricChart({ title, data, color, unit = '' }: MetricChartProps) {
  return (
    <div className="mb-6">
      <h3 className="text-sm text-gray-700 mb-3">{title}</h3>
      <ResponsiveContainer width="100%" height={140}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 11, fill: '#6b7280' }}
            stroke="#d1d5db"
          />
          <YAxis 
            tick={{ fontSize: 11, fill: '#6b7280' }}
            stroke="#d1d5db"
            tickFormatter={(value) => `${Math.round(value)}${unit}`}
          />
          <Tooltip 
            contentStyle={{ 
              fontSize: '12px', 
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '6px'
            }}
            formatter={(value: number) => [`${Math.round(value)}${unit}`, title]}
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

export function MetricsPanel() {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      <h2 className="text-gray-900 mb-5">Operational Metrics</h2>
      
      <MetricChart title="P95 Latency (ms)" data={latencyData} color="#3b82f6" unit="ms" />
      <MetricChart title="Error Rate (%)" data={errorRateData} color="#ef4444" unit="%" />
      <MetricChart title="Request Volume (RPS)" data={requestVolumeData} color="#10b981" unit="" />
      <MetricChart title="Queue Depth" data={queueDepthData} color="#f59e0b" unit="" />
      
      {/* System State */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-sm text-gray-700 mb-3">System State</h3>
        <div className="bg-amber-50 border border-amber-200 rounded-md p-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-amber-500" />
            <span className="text-sm text-gray-900">System Mode: Degraded</span>
          </div>
          <p className="text-sm text-gray-600 leading-relaxed">
            System is operating in degraded mode due to database performance issues. 
            Response times are elevated and some requests are experiencing timeouts.
          </p>
        </div>
      </div>
    </div>
  );
}