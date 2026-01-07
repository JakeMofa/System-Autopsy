# app/core/propagation.py
from typing import TYPE_CHECKING
from .rules import HealthStatus

if TYPE_CHECKING:
    from .simulation import SimulationResult


def propagate_failures(result: "SimulationResult") -> None:
    """
    Propagate degradation through service dependencies.

    Dependency chain:
      API Gateway -> Orders Service -> Database

    Design rules:
    - Deterministic (no randomness)
    - DEGRADED propagates gently
    - UNHEALTHY propagates strongly
    - Propagation must NOT auto-escalate minor incidents
    - Health is NOT recomputed here
    """

    db = result.services.get("database")
    orders = result.services.get("orders_service")
    api = result.services.get("api_gateway")

    # -----------------------------
    # Database → Orders Service
    # -----------------------------
    if db and orders:
        if db.status == HealthStatus.UNHEALTHY:
            # Severe DB issues: blocked threads, retries, queue buildup
            orders.latency_ms += 500
            orders.error_rate_pct += 2.5

        elif db.status == HealthStatus.DEGRADED:
            # Mild DB issues: slower queries, limited contention
            orders.latency_ms += 120
            orders.error_rate_pct += 0.4

    # -----------------------------
    # Orders Service → API Gateway
    # -----------------------------
    if orders and api:
        if orders.status == HealthStatus.UNHEALTHY:
            # Orders meltdown affects API response times & errors
            api.latency_ms += 400
            api.error_rate_pct += 1.5

        elif orders.status == HealthStatus.DEGRADED:
            # Minor downstream slowdown, not an outage
            api.latency_ms += 90
            api.error_rate_pct += 0.25
