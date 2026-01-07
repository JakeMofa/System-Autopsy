# app/api/explain.py

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.simulation import run_baseline_simulation
from app.core.failures import FailureScenario, FAILURE_APPLIERS
from app.core.propagation import propagate_failures

from app.core.explain_payload import build_explain_payload

from app.models.explanation import (
    ExplanationResponse,
    MitigationSuggestion,
)

from app.ai.explainer import generate_ai_explanation

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
    # -------------------------------------------------
    # 1. Run baseline simulation (deterministic)
    # -------------------------------------------------
    result = run_baseline_simulation()

    # -------------------------------------------------
    # 2. Apply failure scenario + propagation
    # -------------------------------------------------
    applier = FAILURE_APPLIERS.get(request.scenario)
    if applier:
        applier(result)
        propagate_failures(result)

    # -------------------------------------------------
    # 3. Build deterministic explain payload
    #    (THIS is the single source of truth for AI)
    # -------------------------------------------------
    payload = build_explain_payload(
        result=result,
        scenario=request.scenario.value,
    )

    print("=== EXPLAIN PAYLOAD ===")
    print(payload)

    # -------------------------------------------------
    # 4. Call AI explainer (bounded, structured)
    # -------------------------------------------------
    ai_result = generate_ai_explanation(payload)

    print("=== AI STRUCTURED RESULT ===")
    print(ai_result)

    # -------------------------------------------------
    # 5. Map AI output → API response
    # -------------------------------------------------
    if ai_result:
        # AI explains:
        # - system mode
        # - why metrics look the way they do
        # - propagation path
        # - mitigations (1–N depending on severity)

        text = [
            ai_result["system_state_summary"],
            ai_result["failure_explanation"],
        ]

        mitigations = [
            MitigationSuggestion(
                action=m["title"],
                description=m["description"],
            )
            for m in ai_result["mitigation_suggestions"]
        ]

        return ExplanationResponse(
            text=text,
            identified_factors=ai_result["identified_factors"],
            mitigation_suggestions=mitigations,
        )

    # -------------------------------------------------
    # 6. Deterministic fallback (NO AI)
    # -------------------------------------------------
    fallback_text = (
        f"System is currently in a {payload['system_mode']} state. "
        "System behavior reflects the current simulation state and "
        "dependency-driven degradation across services."
    )

    return ExplanationResponse(
        text=[fallback_text],
        identified_factors=[],
        mitigation_suggestions=[],
    )
