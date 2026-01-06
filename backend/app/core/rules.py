# app/core/rules.py

from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


# Latency thresholds (ms)
LATENCY_DEGRADED_MS = 300
LATENCY_UNHEALTHY_MS = 900

# Error rate thresholds (fraction 0–1)
ERROR_RATE_DEGRADED = 0.03    # 3%
ERROR_RATE_UNHEALTHY = 0.12   # 12%


def evaluate_health(latency_ms: float, error_rate_pct: float) -> HealthStatus:
    if (
        latency_ms >= LATENCY_UNHEALTHY_MS
        or error_rate_pct >= ERROR_RATE_UNHEALTHY
    ):
        return HealthStatus.UNHEALTHY

    if (
        latency_ms >= LATENCY_DEGRADED_MS
        or error_rate_pct >= ERROR_RATE_DEGRADED
    ):
        return HealthStatus.DEGRADED

    return HealthStatus.HEALTHY
