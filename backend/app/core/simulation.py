from typing import Dict, List, Optional
from dataclasses import dataclass
import random

from .rules import evaluate_health
from .propagation import propagate_failures


# -----------------------------
# Data Models
# -----------------------------

@dataclass
class ServiceState:
    name: str
    latency_ms: float
    error_rate_pct: float
    status: str


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
    Baseline is allowed to be fully HEALTHY.
    """

    services: Dict[str, ServiceState] = {}

    api_latency = generate_latency(80, 20)
    orders_latency = generate_latency(120, 30)
    db_latency = generate_latency(100, 25)
    external_latency = generate_latency(150, 40)

    api_errors = generate_error_rate(0.002, 0.001)
    orders_errors = generate_error_rate(0.005, 0.002)
    db_errors = generate_error_rate(0.003, 0.001)
    external_errors = generate_error_rate(0.007, 0.003)

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

    metrics = {
        "latency_ms": [
            {"time": i, "value": generate_latency(120, 30)}
            for i in range(30)
        ],
        "error_rate_pct": [
            {"time": i, "value": generate_error_rate(0.005, 0.002)}
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

    return SimulationResult(services=services, metrics=metrics)


# -----------------------------
# Scenario-Aware Simulation
# -----------------------------

def run_simulation(scenario: Optional[str]) -> SimulationResult:
    """
    Runs a scenario-aware simulation.

    Rules:
    - Baseline may be all HEALTHY
    - Any scenario MUST produce visible degradation
    - Scenario applies local damage only
    - Dependency effects are handled in propagation.py
    """

    result = run_baseline_simulation()

    if not scenario:
        return result

    # -----------------------------
    # Database Latency Spike
    # -----------------------------
    if scenario == "Database Latency Spike":
        db = result.services["database"]
        db.latency_ms *= 2.5
        db.error_rate_pct *= 2.0

        for p in result.metrics["queue_depth"]:
            p["value"] = int(p["value"] * 2)

        for p in result.metrics["latency_ms"]:
            p["value"] *= 1.4

    # -----------------------------
    # External Dependency Degradation
    # -----------------------------
    elif scenario == "External Dependency Degradation":
        ext = result.services["external_dependency"]
        ext.latency_ms *= 2.0
        ext.error_rate_pct *= 1.8

        for p in result.metrics["latency_ms"]:
            p["value"] *= 1.2

    # -----------------------------
    # Retry Amplification
    # -----------------------------
    elif scenario == "Retry Amplification":
        orders = result.services["orders_service"]
        orders.latency_ms *= 1.8
        orders.error_rate_pct *= 1.6

        for p in result.metrics["request_volume"]:
            p["value"] = int(p["value"] * 1.6)

        for p in result.metrics["queue_depth"]:
            p["value"] = int(p["value"] * 2.2)

    # -----------------------------
    # Health Evaluation — PASS 1
    # -----------------------------
    for svc in result.services.values():
        svc.status = evaluate_health(svc.latency_ms, svc.error_rate_pct)

    # -----------------------------
    # Dependency Propagation
    # -----------------------------
    propagate_failures(result)

    # -----------------------------
    # Health Evaluation — PASS 2
    # -----------------------------
    for svc in result.services.values():
        svc.status = evaluate_health(svc.latency_ms, svc.error_rate_pct)

    # -----------------------------
    # HARD GUARANTEE:
    # No scenario run may end fully healthy
    # -----------------------------
    if all(svc.status == "healthy" for svc in result.services.values()):
        # Force a visible signal (deterministic, minimal)
        victim = result.services["orders_service"]
        victim.latency_ms += 350
        victim.error_rate_pct += 0.04
        victim.status = evaluate_health(
            victim.latency_ms,
            victim.error_rate_pct,
        )

    return result
