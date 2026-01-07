# app/core/explain_payload.py

from typing import Dict, List
from app.core.simulation import SimulationResult


def compute_trend(values: List[float]) -> str:
    """
    Simple deterministic trend detection.
    """
    if not values:
        return "unknown"

    start = values[0]
    end = values[-1]

    if end > start * 1.2:
        return "increasing"
    if end < start * 0.8:
        return "decreasing"
    return "stable"


def build_explain_payload(result: SimulationResult, scenario: str) -> Dict:
    """
    Build a deterministic, LLM-safe explanation payload.
    """

    # -----------------------------
    # Services summary
    # -----------------------------
    services = []
    for svc in result.services.values():
        services.append({
            "name": svc.name,
            "status": svc.status.value,
            "latency_ms": round(svc.latency_ms, 1),
            "error_rate_pct": round(svc.error_rate_pct, 2),
        })

    # -----------------------------
    # Metric trends
    # -----------------------------
    metric_trends = {
        "p95_latency": compute_trend(
            [p["value"] for p in result.metrics["latency_ms"]]
        ),
        "error_rate": compute_trend(
            [p["value"] for p in result.metrics["error_rate_pct"]]
        ),
        "request_volume": compute_trend(
            [p["value"] for p in result.metrics["request_volume"]]
        ),
        "queue_depth": compute_trend(
            [p["value"] for p in result.metrics["queue_depth"]]
        ),
    }

    # -----------------------------
    # Propagation path (static for now)
    # -----------------------------
    propagation_path = [
        "Database → Orders Service → API Gateway"
    ]

    return {
        "scenario": scenario,
        "system_mode": max(
            (svc["status"] for svc in services),
            key=lambda s: ["healthy", "degraded", "unhealthy"].index(s),
        ),
        "services": services,
        "metric_trends": metric_trends,
        "propagation_path": propagation_path,
    }
