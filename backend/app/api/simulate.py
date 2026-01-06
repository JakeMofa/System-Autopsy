from fastapi import APIRouter

from app.core.simulation import run_baseline_simulation
from app.models.simulation_state import SimulationState
from app.models.topology import SystemTopology, ServiceNode, DependencyEdge
from app.models.metrics import MetricsBundle, MetricPoint

router = APIRouter()


@router.post("/simulate", response_model=SimulationState)
def simulate():
    result = run_baseline_simulation()

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

    metrics = MetricsBundle(
        latency_ms=[MetricPoint(**m) for m in result.metrics["latency_ms"]],
        error_rate_pct=[MetricPoint(**m) for m in result.metrics["error_rate_pct"]],
    )

    system_mode = max(
        (svc.status.value for svc in result.services.values()),
        key=lambda s: ["healthy", "degraded", "unhealthy"].index(s),
    )

    return SimulationState(
        system_mode=system_mode,
        topology=topology,
        metrics=metrics,
    )
