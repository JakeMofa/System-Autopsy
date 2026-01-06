#app/api/explain.py
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.simulation import run_baseline_simulation
from app.core.failures import FailureScenario, FAILURE_APPLIERS
from app.core.propagation import propagate_failures

from app.models.explanation import ExplanationResponse, MitigationSuggestion
from app.ai.explainer import generate_ai_explanation
# Optional later:
# from app.ai.groq_explainer import generate_groq_explanation

router = APIRouter()


class ExplainRequest(BaseModel):
    scenario: FailureScenario


@router.post("/explain", response_model=ExplanationResponse)
def explain(request: ExplainRequest):
    #  Run simulation
    result = run_baseline_simulation()

    applier = FAILURE_APPLIERS.get(request.scenario)
    if applier:
        applier(result)
        propagate_failures(result)

    #  Collect deterministic facts (NOT explanation text)
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

    #  Build structured, bounded summary for AI
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

    # AI-first explanation
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
        # LAST resort only
        text.append(
            "[fallback] System degradation detected based on service health thresholds."
        )

    #  Final response
    return ExplanationResponse(
        text=text,
        identified_factors=factors,
        mitigation_suggestions=mitigations,
    )
