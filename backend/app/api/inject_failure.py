from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.simulation import run_baseline_simulation
from app.core.failures import FailureScenario, FAILURE_APPLIERS
from app.core.propagation import propagate_failures

from app.models.simulation_state import SimulationState
from app.models.topology import SystemTopology, ServiceNode, DependencyEdge
from app.models.metrics import MetricsBundle, MetricPoint

router = APIRouter()


class InjectFailureRequest(BaseModel):
    scenario: FailureScenario


@router.post("/inject-failure", response_model=SimulationState)
def inject_failure(request: InjectFailureRequest):
    #  Start from a clean baseline
    result = run_baseline_simulation()

    #  Apply the requested failure
    applier = FAILURE_APPLIERS.get(request.scenario)
    if applier is None:
        raise HTTPException(status_code=400, detail="Unknown failure scenario")

    applier(result)

    #  Propagate failure effects
    propagate_failures(result)

    #  Build topology
    topology = SystemTopology(
        services=[
            ServiceNode(
                id=key,
                name=svc.name,
                status=svc.status.value,
            )
            for key, svc in result.services.items()
        ],
        dependencies=[
            DependencyEdge(source="api_gateway", target="orders_service"),
            DependencyEdge(source="orders_service", target="database"),
        ],
    )

    # Build metrics
    metrics = MetricsBundle(
        latency_ms=[MetricPoint(**m) for m in result.metrics["latency_ms"]],
        error_rate_pct=[MetricPoint(**m) for m in result.metrics["error_rate_pct"]],
    )

    #  Compute overall system mode
    system_mode = max(
        (svc.status.value for svc in result.services.values()),
        key=lambda s: ["healthy", "degraded", "unhealthy"].index(s),
    )

    #  Return typed response
    return SimulationState(
        system_mode=system_mode,
        topology=topology,
        metrics=metrics,
    )
