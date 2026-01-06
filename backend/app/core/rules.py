from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


# Thresholds that determine degraded mode
LATENCY_DEGRADED_MS = 800
LATENCY_UNHEALTHY_MS = 1500

ERROR_RATE_DEGRADED = 2.0   # percent
ERROR_RATE_UNHEALTHY = 5.0  # percent


def evaluate_health(latency_ms: float, error_rate_pct: float) -> HealthStatus:
    if latency_ms >= LATENCY_UNHEALTHY_MS or error_rate_pct >= ERROR_RATE_UNHEALTHY:
        return HealthStatus.UNHEALTHY

    if latency_ms >= LATENCY_DEGRADED_MS or error_rate_pct >= ERROR_RATE_DEGRADED:
        return HealthStatus.DEGRADED

    return HealthStatus.HEALTHY
