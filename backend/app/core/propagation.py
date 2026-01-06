from typing import TYPE_CHECKING
from .rules import HealthStatus

if TYPE_CHECKING:
    from .simulation import SimulationResult


def propagate_failures(result: "SimulationResult") -> None:
    """
    Propagate degradation through service dependencies.

    Dependency chain:
      API Gateway -> Orders Service -> Database

    IMPORTANT:
    - Do NOT recompute health here
    - Only adjust latency / error rates
    """

    db = result.services.get("database")
    orders = result.services.get("orders_service")
    api = result.services.get("api_gateway")

    # -----------------------------
    # Database → Orders Service
    # -----------------------------
    if db and db.status == HealthStatus.UNHEALTHY:
        if orders:
            orders.latency_ms *= 1.25
            orders.error_rate_pct *= 1.2

    elif db and db.status == HealthStatus.DEGRADED:
        if orders:
            orders.latency_ms *= 1.15
            orders.error_rate_pct *= 1.1

    # -----------------------------
    # Orders Service → API Gateway
    # -----------------------------
    if orders and orders.status == HealthStatus.UNHEALTHY:
        if api:
            api.latency_ms *= 1.2
            api.error_rate_pct *= 1.15

    elif orders and orders.status == HealthStatus.DEGRADED:
        if api:
            api.latency_ms *= 1.1
            api.error_rate_pct *= 1.05
