# app/core/simulation.py

from typing import Dict, List, Optional
from dataclasses import dataclass
import random

from .rules import evaluate_health, HealthStatus


# -----------------------------
# Data Models
# -----------------------------

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


# -----------------------------
# Metric Generators
# -----------------------------

def generate_latency(base: float, variance: float) -> float:
    return max(0.0, random.uniform(base - variance, base + variance))


def generate_error_rate(base: float, variance: float) -> float:
    return max(0.0, random.uniform(base - variance, base + variance))


# -----------------------------
# Baseline Simulation
# -----------------------------

def run_baseline_simulation() -> SimulationResult:
    """
    Runs a clean system simulation with no failures injected.
    Generates synthetic telemetry for a distributed system.
    """

    services: Dict[str, ServiceState] = {}

    # -----------------------------
    # Per-service baseline metrics
    # -----------------------------

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

    # -----------------------------
    # Time-series system metrics
    # -----------------------------

    metrics = {
        "latency_ms": [
            {"time": i, "value": generate_latency(120, 30)}
            for i in range(30)
        ],
        "error_rate_pct": [
            {"time": i, "value": generate_error_rate(0.5, 0.2)}
            for i in range(30)
        ],
        "request_volume": [
            {"time": i, "value": random.randint(300, 600)}
            for i in range(30)
        ],
        "queue_depth": [
            {"time": i, "value": random.randint(5, 40)}
            for i in range(30)
        ],
    }

    return SimulationResult(
        services=services,
        metrics=metrics,
    )


# -----------------------------
# Scenario-Aware Simulation
# -----------------------------

def run_simulation(scenario: Optional[str]) -> SimulationResult:
    """
    Runs a scenario-aware simulation.
    Starts from baseline behavior and applies controlled failure modifiers.
    """

    result = run_baseline_simulation()

    if not scenario:
        return result

    # -----------------------------
    # Database Latency Spike
    # -----------------------------
    if scenario == "Database Latency Spike":
        db = result.services.get("database")
        if db:
            db.latency_ms *= 3
            db.error_rate_pct *= 2
            db.status = evaluate_health(db.latency_ms, db.error_rate_pct)

        for point in result.metrics["queue_depth"]:
            point["value"] *= 2

    # -----------------------------
    # External Dependency Degradation
    # -----------------------------
    elif scenario == "External Dependency Degradation":
        ext = result.services.get("external_dependency")
        if ext:
            ext.latency_ms *= 2
            ext.error_rate_pct *= 1.8
            ext.status = evaluate_health(ext.latency_ms, ext.error_rate_pct)

    # -----------------------------
    # Retry Amplification
    # -----------------------------
    elif scenario == "Retry Amplification":
        orders = result.services.get("orders_service")
        if orders:
            orders.latency_ms *= 1.8
            orders.error_rate_pct *= 1.5
            orders.status = evaluate_health(
                orders.latency_ms, orders.error_rate_pct
            )

        for point in result.metrics["request_volume"]:
            point["value"] = int(point["value"] * 1.6)

        for point in result.metrics["queue_depth"]:
            point["value"] = int(point["value"] * 2.5)

    return result
