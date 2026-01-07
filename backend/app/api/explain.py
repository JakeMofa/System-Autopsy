# app/api/explain.py

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.simulation import run_baseline_simulation
from app.core.failures import FailureScenario, FAILURE_APPLIERS
from app.core.propagation import propagate_failures

from app.models.explanation import ExplanationResponse, MitigationSuggestion
from app.ai.explainer import generate_ai_explanation

#  deterministic explain payload
from app.core.explain_payload import build_explain_payload

# Optional later:
# from app.ai.groq_explainer import generate_groq_explanation

router = APIRouter()


# -----------------------------
# Request Model
# -----------------------------

class ExplainRequest(BaseModel):
    scenario: FailureScenario


# -----------------------------
# Explain Endpoint
# -----------------------------

@router.post("/explain", response_model=ExplanationResponse)
def explain(request: ExplainRequest):
    # -----------------------------
    # 1. Run baseline simulation
    # -----------------------------
    result = run_baseline_simulation()

    # -----------------------------
    # 2. Apply failure scenario
    # -----------------------------
    applier = FAILURE_APPLIERS.get(request.scenario)
    if applier:
        applier(result)
        propagate_failures(result)

    # -----------------------------
    # 3.  Build deterministic explain payload (NO AI)
    # -----------------------------
    payload = build_explain_payload(result, request.scenario.value)
    print("=== EXPLAIN PAYLOAD ===")
    print(payload)

    # -----------------------------
    # 4. Existing deterministic factors & mitigations
    #    (kept for now — will be replaced later)
    # -----------------------------
    factors = []
    mitigations = []

    db = result.services["database"]
    orders = result.services["orders_service"]

    if db.status.value in ("degraded", "unhealthy"):
        factors.append("Database latency spike")
        mitigations.append(
            MitigationSuggestion(
                action="Increase database capacity",
                description="Scale database resources or optimize slow queries.",
            )
        )

    if orders.status.value in ("degraded", "unhealthy"):
        factors.append("Downstream dependency degradation")
        mitigations.append(
            MitigationSuggestion(
                action="Add circuit breakers",
                description="Prevent cascading failures by failing fast on downstream timeouts.",
            )
        )

    # -----------------------------
    # 5. Existing summary for AI (temporary)
    # -----------------------------
    summary = {
        "system_mode": max(
            svc.status.value for svc in result.services.values()
        ),
        "services": {
            key: {
                "latency_ms": svc.latency_ms,
                "error_rate_pct": svc.error_rate_pct,
                "status": svc.status.value,
            }
            for key, svc in result.services.items()
        },
        "identified_factors": factors,
        "mitigations": [m.action for m in mitigations],
    }

    # -----------------------------
    # 6. AI explanation (unchanged for now)
    # -----------------------------
    text = []

    ai_text = generate_ai_explanation(summary)
    ai_source = "ollama"

    # Optional future Groq fallback
    # if not ai_text:
    #     ai_text = generate_groq_explanation(summary)
    #     ai_source = "groq"

    if ai_text:
        text.append(f"[AI:{ai_source}] {ai_text}")
    else:
        text.append(
            "[fallback] System degradation detected based on service health thresholds."
        )

    # -----------------------------
    # 7. Final response
    # -----------------------------
    return ExplanationResponse(
        text=text,
        identified_factors=factors,
        mitigation_suggestions=mitigations,
    )
