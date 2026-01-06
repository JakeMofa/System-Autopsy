from enum import Enum
from typing import Callable

from .simulation import SimulationResult, ServiceState
from .rules import evaluate_health


class FailureScenario(str, Enum):
    DATABASE_LATENCY_SPIKE = "database_latency_spike"
    EXTERNAL_DEPENDENCY_DEGRADATION = "external_dependency_degradation"
    RETRY_AMPLIFICATION = "retry_amplification"


def apply_database_latency_spike(result: SimulationResult) -> None:
    """
    Simulate a sudden database latency and error spike.
    """
    db = result.services["database"]

    db.latency_ms += 1400
    db.error_rate_pct += 6.0
    db.status = evaluate_health(db.latency_ms, db.error_rate_pct)


def apply_external_dependency_degradation(result: SimulationResult) -> None:
    """
    Simulate an external API becoming slow and flaky.
    """
    ext = result.services["external_dependency"]

    ext.latency_ms += 600
    ext.error_rate_pct += 2.0
    ext.status = evaluate_health(ext.latency_ms, ext.error_rate_pct)


FAILURE_APPLIERS: dict[FailureScenario, Callable[[SimulationResult], None]] = {
    FailureScenario.DATABASE_LATENCY_SPIKE: apply_database_latency_spike,
    FailureScenario.EXTERNAL_DEPENDENCY_DEGRADATION: apply_external_dependency_degradation,
}
