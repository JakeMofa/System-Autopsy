# app/api/simulate.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.core.simulation import run_simulation
from app.models.simulation_state import SimulationState
from app.models.topology import SystemTopology, ServiceNode, DependencyEdge
from app.models.metrics import MetricsBundle, MetricPoint

router = APIRouter()


# -----------------------------
# Request Model
# -----------------------------

class SimulateRequest(BaseModel):
    scenario: Optional[str] = None


# -----------------------------
# Simulation Endpoint
# -----------------------------

@router.post("/simulate", response_model=SimulationState)
def simulate(req: SimulateRequest):
    """
    Runs a system simulation.
    - If scenario is None → baseline behavior
    - If scenario is provided → scenario-aware degradation
    """

    # key 
    result = run_simulation(req.scenario)

    # -----------------------------
    # Build topology response
    # -----------------------------

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

    # -----------------------------
    # Build metrics response
    # -----------------------------

    metrics = MetricsBundle(
        latency_ms=[
            MetricPoint(**m) for m in result.metrics["latency_ms"]
        ],
        error_rate_pct=[
            MetricPoint(**m) for m in result.metrics["error_rate_pct"]
        ],
        request_volume=[
            MetricPoint(**m) for m in result.metrics["request_volume"]
        ],
        queue_depth=[
            MetricPoint(**m) for m in result.metrics["queue_depth"]
        ],
    )

    # -----------------------------
    # Derive system mode
    # -----------------------------

    system_mode = max(
        (svc.status.value for svc in result.services.values()),
        key=lambda s: ["healthy", "degraded", "unhealthy"].index(s),
    )

    return SimulationState(
        system_mode=system_mode,
        topology=topology,
        metrics=metrics,
    )
