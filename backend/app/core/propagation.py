##app/core/propagation
from .simulation import SimulationResult
from .rules import evaluate_health, HealthStatus


def propagate_failures(result: SimulationResult) -> None:
    """
    Propagate degradation through service dependencies.
    """

    db = result.services["database"]
    orders = result.services["orders_service"]
    api = result.services["api_gateway"]

    # Database impacts Orders Service
    if db.status in (HealthStatus.DEGRADED, HealthStatus.UNHEALTHY):
        orders.latency_ms += db.latency_ms * 0.4
        orders.error_rate_pct += db.error_rate_pct * 0.6
        orders.status = evaluate_health(
            orders.latency_ms, orders.error_rate_pct
        )

    # Orders Service impacts API Gateway
    if orders.status in (HealthStatus.DEGRADED, HealthStatus.UNHEALTHY):
        api.latency_ms += orders.latency_ms * 0.2
        api.error_rate_pct += orders.error_rate_pct * 0.3
        api.status = evaluate_health(
            api.latency_ms, api.error_rate_pct
        )
