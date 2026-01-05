//ExplanationPanel/tsx
export function ExplanationPanel() {
  // All data below would come from /explain API endpoint response
  const explanation = {
    text: [
      "The current system degradation originated from a database latency spike at approximately 15 minutes ago. The initial slowdown triggered a cascade of retry attempts from the Orders Service, which amplified the load on the already-saturated database.",
      "As database response times increased from ~50ms to over 300ms, connection pool exhaustion began occurring in the Orders Service. This caused thread pool saturation, leading to request queueing and elevated error rates across the system.",
      "The retry amplification effect is particularly notable: each failed request triggers 3 retry attempts with exponential backoff, but the backoff configuration (max 2 seconds) is insufficient for the current database recovery time, resulting in sustained elevated load that prevents normal operation from resuming."
    ],
    identifiedFactors: [
      'Database saturation',
      'Retry amplification',
      'Thread pool exhaustion',
    ],
    mitigationSuggestions: [
      {
        action: 'Limit retries',
        description: 'Reduce retry attempts from 3 to 1 and increase backoff duration to 5-10 seconds',
      },
      {
        action: 'Enable read-only mode',
        description: 'Switch database to read-only mode to reduce write contention and allow recovery',
      },
      {
        action: 'Disable non-critical features',
        description: 'Temporarily disable recommendation engine and analytics processing to reduce load',
      },
    ],
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 flex flex-col h-[calc(100vh-140px)]">
      <h2 className="text-gray-900 mb-4">Failure Explanation</h2>
      
      <div className="flex-1 overflow-y-auto pr-2">
        <div className="mb-1">
          <p className="text-xs text-gray-500 mb-3">AI-Assisted Explanation (Informational Only)</p>
        </div>
        
        {/* Main explanation text */}
        <div className="bg-gray-50 border border-gray-200 rounded-md p-4 mb-5">
          {explanation.text.map((paragraph, idx) => (
            <p key={idx} className="text-sm text-gray-900 leading-relaxed mb-3 last:mb-0">
              {paragraph}
            </p>
          ))}
        </div>
        
        {/* Identified Factors */}
        <div className="mb-5">
          <h3 className="text-sm text-gray-700 mb-3">Identified Factors</h3>
          <ul className="space-y-2">
            {explanation.identifiedFactors.map((factor, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-gray-900">
                <span className="text-gray-400 mt-0.5">•</span>
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>
        
        {/* Mitigation Suggestions */}
        <div>
          <h3 className="text-sm text-gray-700 mb-3">Mitigation Suggestions</h3>
          <div className="space-y-3">
            {explanation.mitigationSuggestions.map((suggestion, idx) => (
              <div 
                key={idx}
                className="border border-gray-200 rounded-md p-3 bg-white"
              >
                <h4 className="text-sm text-gray-900 mb-1">{suggestion.action}</h4>
                <p className="text-sm text-gray-600">{suggestion.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}