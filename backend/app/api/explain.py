from fastapi import APIRouter
from pydantic import BaseModel

from app.core.simulation import run_baseline_simulation
from app.core.failures import FailureScenario, FAILURE_APPLIERS
from app.core.propagation import propagate_failures
from app.models.explanation import ExplanationResponse, MitigationSuggestion

router = APIRouter()


class ExplainRequest(BaseModel):
    scenario: FailureScenario


@router.post("/explain", response_model=ExplanationResponse)
def explain(request: ExplainRequest):
    # Run baseline
    result = run_baseline_simulation()

    #  Apply failure
    applier = FAILURE_APPLIERS.get(request.scenario)
    if applier:
        applier(result)
        propagate_failures(result)

    # Deterministic explanation logic
    text = []
    factors = []
    mitigations = []

    db = result.services["database"]
    orders = result.services["orders_service"]

    if db.status.value in ("degraded", "unhealthy"):
        text.append(
            "Database latency exceeded acceptable thresholds, causing request backlog."
        )
        factors.append("Database latency spike")

        mitigations.append(
            MitigationSuggestion(
                action="Increase database capacity",
                description="Scale database resources or optimize slow queries.",
            )
        )

    if orders.status.value in ("degraded", "unhealthy"):
        text.append(
            "Orders Service experienced increased latency due to downstream dependency issues."
        )
        factors.append("Downstream dependency degradation")

        mitigations.append(
            MitigationSuggestion(
                action="Add circuit breakers",
                description="Prevent cascading failures by failing fast on downstream timeouts.",
            )
        )

    if not text:
        text.append("System is operating within normal parameters.")

    return ExplanationResponse(
        text=text,
        identified_factors=factors,
        mitigation_suggestions=mitigations,
    )
