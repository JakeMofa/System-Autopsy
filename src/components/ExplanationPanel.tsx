// src/components/ExplanationPanel.tsx

interface MitigationSuggestion {
  action: string;
  description: string;
}

interface Explanation {
  text?: string[];
  identifiedFactors?: string[];
  mitigationSuggestions?: MitigationSuggestion[];
}

interface ExplanationPanelProps {
  explanation: Explanation | null;
  loading: boolean;
}

export function ExplanationPanel({
  explanation,
  loading,
}: ExplanationPanelProps) {
  // -----------------------------
  // Loading state
  // -----------------------------
  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h2 className="text-gray-900 mb-4">Failure Explanation</h2>
        <p className="text-sm text-gray-500">
          Generating explanation…
        </p>
      </div>
    );
  }

  // -----------------------------
  // Empty state (no explanation yet)
  // -----------------------------
  if (!explanation) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-5">
        <h2 className="text-gray-900 mb-4">Failure Explanation</h2>
        <p className="text-sm text-gray-500">
          Click <strong>Explain Failure</strong> to generate an explanation.
        </p>
      </div>
    );
  }

  // -----------------------------
  // HARD DEFENSIVE NORMALIZATION
  // -----------------------------
  const text = Array.isArray(explanation.text)
    ? explanation.text
    : [];

  const identifiedFactors = Array.isArray(explanation.identifiedFactors)
    ? explanation.identifiedFactors
    : [];

  const mitigationSuggestions = Array.isArray(
    explanation.mitigationSuggestions
  )
    ? explanation.mitigationSuggestions
    : [];

  // -----------------------------
  // Render explanation
  // -----------------------------
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 flex flex-col h-[calc(100vh-140px)]">
      <h2 className="text-gray-900 mb-4">Failure Explanation</h2>

      <div className="flex-1 overflow-y-auto pr-2">
        <p className="text-xs text-gray-500 mb-3">
          AI-Assisted Explanation (Informational Only)
        </p>

        {/* -----------------------------
            Main explanation text
           ----------------------------- */}
        {text.length > 0 && (
          <div className="bg-gray-50 border border-gray-200 rounded-md p-4 mb-5">
            {text.map((paragraph, idx) => (
              <p
                key={idx}
                className="text-sm text-gray-900 leading-relaxed mb-3 last:mb-0"
              >
                {paragraph}
              </p>
            ))}
          </div>
        )}

        {/* -----------------------------
            Identified Factors
           ----------------------------- */}
        {identifiedFactors.length > 0 && (
          <div className="mb-5">
            <h3 className="text-sm text-gray-700 mb-3">
              Identified Factors
            </h3>
            <ul className="space-y-2">
              {identifiedFactors.map((factor, idx) => (
                <li
                  key={idx}
                  className="flex items-start gap-2 text-sm text-gray-900"
                >
                  <span className="text-gray-400 mt-0.5">•</span>
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* -----------------------------
            Mitigation Suggestions
           ----------------------------- */}
        {mitigationSuggestions.length > 0 && (
          <div>
            <h3 className="text-sm text-gray-700 mb-3">
              Mitigation Suggestions
            </h3>
            <div className="space-y-3">
              {mitigationSuggestions.map((s, idx) => (
                <div
                  key={idx}
                  className="border border-gray-200 rounded-md p-3 bg-white"
                >
                  <h4 className="text-sm text-gray-900 mb-1">
                    {s.action}
                  </h4>
                  <p className="text-sm text-gray-600">
                    {s.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* -----------------------------
            Fallback if AI returned nothing useful
           ----------------------------- */}
        {text.length === 0 &&
          identifiedFactors.length === 0 &&
          mitigationSuggestions.length === 0 && (
            <p className="text-sm text-gray-500">
              No explanation details were generated for this scenario.
            </p>
          )}
      </div>
    </div>
  );
}