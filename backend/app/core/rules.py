# app/core/rules.py

from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


# Latency thresholds (ms)
LATENCY_DEGRADED_MS = 300
LATENCY_UNHEALTHY_MS = 900

# Error rate thresholds (PERCENT, 0–100)
ERROR_RATE_DEGRADED_PCT = 3.0    # 3%
ERROR_RATE_UNHEALTHY_PCT = 8.0   # 8%


def evaluate_health(latency_ms: float, error_rate_pct: float) -> HealthStatus:
    """
    error_rate_pct is expected to be in PERCENT (0–100).
    """

    if (
        latency_ms >= LATENCY_UNHEALTHY_MS
        or error_rate_pct >= ERROR_RATE_UNHEALTHY_PCT
    ):
        return HealthStatus.UNHEALTHY

    if (
        latency_ms >= LATENCY_DEGRADED_MS
        or error_rate_pct >= ERROR_RATE_DEGRADED_PCT
    ):
        return HealthStatus.DEGRADED

    return HealthStatus.HEALTHY
