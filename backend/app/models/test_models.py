from app.models.topology import SystemTopology, ServiceNode, DependencyEdge
from app.models.metrics import MetricsBundle, MetricPoint
from app.models.simulation_state import SimulationState
from app.models.explanation import ExplanationResponse, MitigationSuggestion


def test_topology():
    topology = SystemTopology(
        services=[
            ServiceNode(id="api", name="API Gateway", status="healthy"),
            ServiceNode(id="orders", name="Orders Service", status="degraded"),
            ServiceNode(id="db", name="Database", status="unhealthy"),
        ],
        dependencies=[
            DependencyEdge(source="api", target="orders"),
            DependencyEdge(source="orders", target="db"),
        ],
    )
    print("\n=== TOPOLOGY ===")
    print(topology)


def test_metrics():
    metrics = MetricsBundle(
        latency_ms=[
            MetricPoint(time=0, value=120.5),
            MetricPoint(time=1, value=135.2),
        ],
        error_rate_pct=[
            MetricPoint(time=0, value=0.4),
            MetricPoint(time=1, value=0.7),
        ],
    )
    print("\n=== METRICS ===")
    print(metrics)


def test_simulation_state():
    topology = SystemTopology(
        services=[
            ServiceNode(id="api", name="API Gateway", status="healthy"),
        ],
        dependencies=[],
    )

    metrics = MetricsBundle(
        latency_ms=[MetricPoint(time=0, value=100.0)],
        error_rate_pct=[MetricPoint(time=0, value=0.2)],
    )

    state = SimulationState(
        system_mode="degraded",
        topology=topology,
        metrics=metrics,
    )

    print("\n=== SIMULATION STATE ===")
    print(state)


def test_explanation():
    explanation = ExplanationResponse(
        text=[
            "Database latency spiked beyond acceptable thresholds.",
            "Retry amplification caused sustained load on dependent services.",
        ],
        identified_factors=[
            "Database saturation",
            "Retry amplification",
        ],
        mitigation_suggestions=[
            MitigationSuggestion(
                action="Limit retries",
                description="Reduce retries and increase backoff window.",
            )
        ],
    )

    print("\n=== EXPLANATION ===")
    print(explanation)


if __name__ == "__main__":
    test_topology()
    test_metrics()
    test_simulation_state()
    test_explanation()
