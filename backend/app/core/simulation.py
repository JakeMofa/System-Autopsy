from typing import Dict, List
from dataclasses import dataclass
import random

from .rules import evaluate_health, HealthStatus


@dataclass
class ServiceState:
    name: str
    latency_ms: float
    error_rate_pct: float
    status: HealthStatus


@dataclass
class SimulationResult:
    services: Dict[str, ServiceState]
    metrics: Dict[str, List[Dict[str, float]]]


def generate_latency(base: float, variance: float) -> float:
    return max(0.0, random.uniform(base - variance, base + variance))


def generate_error_rate(base: float, variance: float) -> float:
    return max(0.0, random.uniform(base - variance, base + variance))


def run_baseline_simulation() -> SimulationResult:
    """
    Runs a clean system simulation with no failures injected.
    """

    services = {}

    # Simulated baseline metrics
    api_latency = generate_latency(80, 20)
    orders_latency = generate_latency(120, 30)
    db_latency = generate_latency(100, 25)
    external_latency = generate_latency(150, 40)

    api_errors = generate_error_rate(0.2, 0.1)
    orders_errors = generate_error_rate(0.5, 0.2)
    db_errors = generate_error_rate(0.3, 0.1)
    external_errors = generate_error_rate(0.7, 0.3)

    services["api_gateway"] = ServiceState(
        name="API Gateway",
        latency_ms=api_latency,
        error_rate_pct=api_errors,
        status=evaluate_health(api_latency, api_errors),
    )

    services["orders_service"] = ServiceState(
        name="Orders Service",
        latency_ms=orders_latency,
        error_rate_pct=orders_errors,
        status=evaluate_health(orders_latency, orders_errors),
    )

    services["database"] = ServiceState(
        name="Database",
        latency_ms=db_latency,
        error_rate_pct=db_errors,
        status=evaluate_health(db_latency, db_errors),
    )

    services["external_dependency"] = ServiceState(
        name="External Dependency",
        latency_ms=external_latency,
        error_rate_pct=external_errors,
        status=evaluate_health(external_latency, external_errors),
    )

    # Simple time-series metric placeholders
    metrics = {
        "latency_ms": [
            {"time": i, "value": generate_latency(120, 30)} for i in range(30)
        ],
        "error_rate_pct": [
            {"time": i, "value": generate_error_rate(0.5, 0.2)} for i in range(30)
        ],
    }

    return SimulationResult(services=services, metrics=metrics)


