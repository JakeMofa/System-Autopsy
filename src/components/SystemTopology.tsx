//SYSTEMTopology/tsx
import { useState } from 'react';
import { ArrowDown, AlertTriangle } from 'lucide-react';

interface Service {
  id: string;
  name: string;
  status: 'normal' | 'degraded' | 'unhealthy';
}

// Mock data - in production this would come from /simulate API response
const services: Service[] = [
  { id: '1', name: 'API Gateway', status: 'normal' },
  { id: '2', name: 'Orders Service', status: 'degraded' },
  { id: '3', name: 'Database', status: 'unhealthy' },
  { id: '4', name: 'External Dependency', status: 'normal' },
];

// Scenarios would be fetched from /scenarios API endpoint
const scenarios = [
  'Database Latency Spike',
  'External Dependency Degradation',
  'Retry Amplification',
];

export function SystemTopology() {
  const [selectedScenario, setSelectedScenario] = useState(scenarios[0]);

  const handleInjectFailure = () => {
    // This would POST to /simulate endpoint with the selected scenario
    console.log('Injecting failure scenario:', selectedScenario);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      <h2 className="text-gray-900 mb-4">System Overview</h2>
      
      {/* Status legend */}
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
      
      {/* Service topology diagram */}
      <div className="mb-6 space-y-3">
        {services.map((service, idx) => (
          <div key={service.id}>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded border border-gray-200">
              <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                service.status === 'normal' ? 'bg-green-500' :
                service.status === 'degraded' ? 'bg-yellow-500' :
                'bg-red-500'
              }`} />
              <span className="text-sm text-gray-900">{service.name}</span>
            </div>
            {idx < services.length - 1 && (
              <div className="flex justify-center py-1">
                <ArrowDown className="w-4 h-4 text-gray-400" />
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Failure scenario controls */}
      <div className="space-y-3">
        <div>
          <label className="block text-sm text-gray-700 mb-2">
            Failure Scenario
          </label>
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {scenarios.map((scenario) => (
              <option key={scenario} value={scenario}>
                {scenario}
              </option>
            ))}
          </select>
        </div>
        
        <button 
          onClick={handleInjectFailure}
          className="w-full bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-md flex items-center justify-center gap-2 transition-colors"
        >
          <AlertTriangle className="w-4 h-4" />
          Inject Failure
        </button>
      </div>
    </div>
  );
}