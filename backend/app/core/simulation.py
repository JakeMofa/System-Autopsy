# app/core/simulation.py
from typing import Dict, List, Optional
from dataclasses import dataclass
import random

from app.core.rules import evaluate_health, HealthStatus
from .propagation import propagate_failures


# -----------------------------
# Data Models
# -----------------------------

@dataclass
class ServiceState:
    name: str
    latency_ms: float
    error_rate_pct: float  # percent (0–100)
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


def generate_error_rate_pct(base: float, variance: float) -> float:
    """
    Error rate as percent (0–100).
    Example: base=0.5 means ~0.5%
    """
    return max(0.0, random.uniform(base - variance, base + variance))


# -----------------------------
# Baseline Simulation
# -----------------------------

def run_baseline_simulation() -> SimulationResult:
    """
    Clean, healthy baseline.
    """

    services: Dict[str, ServiceState] = {}

    api_latency = generate_latency(80, 20)
    orders_latency = generate_latency(120, 30)
    db_latency = generate_latency(100, 25)
    external_latency = generate_latency(150, 40)

    api_errors = generate_error_rate_pct(0.3, 0.2)
    orders_errors = generate_error_rate_pct(0.6, 0.4)
    db_errors = generate_error_rate_pct(0.4, 0.3)
    external_errors = generate_error_rate_pct(0.8, 0.5)

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
            {"time": i, "value": generate_error_rate_pct(0.6, 0.4)}
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
    Scenario-aware simulation with severity tiers.

    Severity is chosen ONCE per run:
    - minor
    - major
    - critical
    """

    result = run_baseline_simulation()

    if not scenario:
        return result

    severity = random.choices(
        ["minor", "major", "critical"],
        weights=[0.5, 0.35, 0.15],
        k=1
    )[0]

    # -----------------------------
    # Database Latency Spike
    # -----------------------------
    if scenario == "Database Latency Spike":
        db = result.services["database"]

        if severity == "minor":
            db.latency_ms = random.uniform(400, 700)
            db.error_rate_pct = random.uniform(1.5, 3.5)

        elif severity == "major":
            db.latency_ms = random.uniform(800, 1200)
            db.error_rate_pct = random.uniform(4.0, 6.5)

        else:  # critical
            db.latency_ms = random.uniform(1300, 1800)
            db.error_rate_pct = random.uniform(7.0, 10.0)

        for p in result.metrics["queue_depth"]:
            p["value"] = int(p["value"] * random.uniform(1.5, 3.0))

        for p in result.metrics["latency_ms"]:
            p["value"] *= random.uniform(1.2, 1.8)

        for p in result.metrics["error_rate_pct"]:
            p["value"] *= random.uniform(1.5, 4.0)

    # -----------------------------
    # External Dependency Degradation
    # -----------------------------
    elif scenario == "External Dependency Degradation":
        ext = result.services["external_dependency"]

        if severity == "minor":
            ext.latency_ms = random.uniform(350, 600)
            ext.error_rate_pct = random.uniform(1.5, 3.0)

        elif severity == "major":
            ext.latency_ms = random.uniform(650, 950)
            ext.error_rate_pct = random.uniform(3.5, 6.0)

        else:  # critical
            ext.latency_ms = random.uniform(1000, 1400)
            ext.error_rate_pct = random.uniform(6.5, 9.0)

        for p in result.metrics["latency_ms"]:
            p["value"] *= random.uniform(1.2, 1.6)

        for p in result.metrics["error_rate_pct"]:
            p["value"] *= random.uniform(1.5, 3.5)

    # -----------------------------
    # Retry Amplification
    # -----------------------------
    elif scenario == "Retry Amplification":
        orders = result.services["orders_service"]

        if severity == "minor":
            orders.latency_ms = random.uniform(350, 600)
            orders.error_rate_pct = random.uniform(2.0, 4.0)

        elif severity == "major":
            orders.latency_ms = random.uniform(650, 950)
            orders.error_rate_pct = random.uniform(4.5, 7.0)

        else:  # critical
            orders.latency_ms = random.uniform(1000, 1500)
            orders.error_rate_pct = random.uniform(7.5, 10.0)

        for p in result.metrics["request_volume"]:
            p["value"] = int(p["value"] * random.uniform(1.4, 2.5))

        for p in result.metrics["queue_depth"]:
            p["value"] = int(p["value"] * random.uniform(1.8, 3.5))

        for p in result.metrics["error_rate_pct"]:
            p["value"] *= random.uniform(1.8, 4.0)

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
    # CLAMP ERROR RATES (CRITICAL FIX)
    # -----------------------------
    for svc in result.services.values():
        svc.error_rate_pct = min(svc.error_rate_pct, 15.0)

    # -----------------------------
    # Health Evaluation — PASS 2
    # -----------------------------
    for svc in result.services.values():
        svc.status = evaluate_health(svc.latency_ms, svc.error_rate_pct)

    # -----------------------------
    # HARD GUARANTEE
    # -----------------------------
    if all(svc.status == HealthStatus.HEALTHY for svc in result.services.values()):
        victim = result.services["orders_service"]
        victim.latency_ms = max(victim.latency_ms, 600.0)
        victim.error_rate_pct = max(victim.error_rate_pct, 4.0)
        victim.status = evaluate_health(victim.latency_ms, victim.error_rate_pct)

    return result
