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
    # IMPORTANT:
    # error_rate_pct is a FRACTION (0.0–1.0), not 0–100.
    # Example: 0.02 means 2%
    error_rate_pct: float
    status: HealthStatus


@dataclass
class SimulationResult:
    services: Dict[str, ServiceState]
    metrics: Dict[str, List[Dict[str, float]]]


# -----------------------------
# Helpers
# -----------------------------

def generate_latency(base: float, variance: float) -> float:
    return max(0.0, random.uniform(base - variance, base + variance))


def generate_error_rate(base: float, variance: float) -> float:
    """
    Error rate as FRACTION (0.0–1.0).
    Example: base=0.006 means ~0.6%
    """
    return max(0.0, random.uniform(base - variance, base + variance))


def normalize_scenario(s: Optional[str]) -> Optional[str]:
    """
    Accept either:
      - enum values: database_latency_spike
      - UI display:  Database Latency Spike
    and normalize to enum value.
    """
    if not s:
        return None

    mapping = {
        "Database Latency Spike": "database_latency_spike",
        "External Dependency Degradation": "external_dependency_degradation",
        "Retry Amplification": "retry_amplification",
    }

    if s in mapping:
        return mapping[s]

    # best-effort normalization
    lowered = s.strip().lower().replace(" ", "_")
    return lowered


# -----------------------------
# Baseline Simulation
# -----------------------------

def run_baseline_simulation() -> SimulationResult:
    """
    Clean, healthy baseline (fresh data every run).
    """

    services: Dict[str, ServiceState] = {}

    api_latency = generate_latency(80, 20)
    orders_latency = generate_latency(120, 30)
    db_latency = generate_latency(100, 25)
    external_latency = generate_latency(150, 40)

    # FRACTIONS (0–1)
    api_errors = generate_error_rate(0.003, 0.002)       # ~0.3%
    orders_errors = generate_error_rate(0.006, 0.004)    # ~0.6%
    db_errors = generate_error_rate(0.004, 0.003)        # ~0.4%
    external_errors = generate_error_rate(0.008, 0.005)  # ~0.8%

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
        "latency_ms": [{"time": i, "value": generate_latency(120, 30)} for i in range(30)],
        # FRACTIONS (0–1)
        "error_rate_pct": [{"time": i, "value": generate_error_rate(0.006, 0.004)} for i in range(30)],
        "request_volume": [{"time": i, "value": random.randint(300, 600)} for i in range(30)],
        "queue_depth": [{"time": i, "value": random.randint(5, 40)} for i in range(30)],
    }

    return SimulationResult(services=services, metrics=metrics)


# -----------------------------
# Scenario-Aware Simulation
# -----------------------------

def run_simulation(scenario: Optional[str]) -> SimulationResult:
    """
    Scenario-aware simulation with severity tiers.

    scenario values expected (enum):
      - database_latency_spike
      - external_dependency_degradation
      - retry_amplification

    We also accept UI display strings and normalize them.
    """

    result = run_baseline_simulation()

    scenario_norm = normalize_scenario(scenario)
    if not scenario_norm:
        return result

    severity = random.choices(
        ["minor", "major", "critical"],
        weights=[0.5, 0.35, 0.15],
        k=1,
    )[0]

    # -----------------------------
    # Database Latency Spike
    # -----------------------------
    if scenario_norm == "database_latency_spike":
        db = result.services["database"]

        if severity == "minor":
            db.latency_ms = random.uniform(400, 700)
            db.error_rate_pct = random.uniform(0.015, 0.035)   # 1.5%–3.5%
        elif severity == "major":
            db.latency_ms = random.uniform(800, 1200)
            db.error_rate_pct = random.uniform(0.040, 0.065)   # 4.0%–6.5%
        else:  # critical
            db.latency_ms = random.uniform(1300, 1800)
            db.error_rate_pct = random.uniform(0.070, 0.100)   # 7%–10%

        for p in result.metrics["queue_depth"]:
            p["value"] = int(p["value"] * random.uniform(1.5, 3.0))

        for p in result.metrics["latency_ms"]:
            p["value"] *= random.uniform(1.2, 1.8)

        for p in result.metrics["error_rate_pct"]:
            p["value"] *= random.uniform(1.5, 4.0)

    # -----------------------------
    # External Dependency Degradation
    # -----------------------------
    elif scenario_norm == "external_dependency_degradation":
        ext = result.services["external_dependency"]

        if severity == "minor":
            ext.latency_ms = random.uniform(350, 600)
            ext.error_rate_pct = random.uniform(0.015, 0.030)
        elif severity == "major":
            ext.latency_ms = random.uniform(650, 950)
            ext.error_rate_pct = random.uniform(0.035, 0.060)
        else:  # critical
            ext.latency_ms = random.uniform(1000, 1400)
            ext.error_rate_pct = random.uniform(0.065, 0.090)

        for p in result.metrics["latency_ms"]:
            p["value"] *= random.uniform(1.2, 1.6)

        for p in result.metrics["error_rate_pct"]:
            p["value"] *= random.uniform(1.5, 3.5)

    # -----------------------------
    # Retry Amplification
    # -----------------------------
    elif scenario_norm == "retry_amplification":
        orders = result.services["orders_service"]

        if severity == "minor":
            orders.latency_ms = random.uniform(350, 600)
            orders.error_rate_pct = random.uniform(0.020, 0.040)
        elif severity == "major":
            orders.latency_ms = random.uniform(650, 950)
            orders.error_rate_pct = random.uniform(0.045, 0.070)
        else:  # critical
            orders.latency_ms = random.uniform(1000, 1500)
            orders.error_rate_pct = random.uniform(0.075, 0.100)

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
    # Clamp error rate (fraction)
    # -----------------------------
    for svc in result.services.values():
        svc.error_rate_pct = min(max(svc.error_rate_pct, 0.0), 0.15)  # cap at 15%

    # -----------------------------
    # Health Evaluation — PASS 2
    # -----------------------------
    for svc in result.services.values():
        svc.status = evaluate_health(svc.latency_ms, svc.error_rate_pct)

    return result