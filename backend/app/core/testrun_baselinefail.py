from app.core.simulation import run_baseline_simulation
from app.core.failures import FailureScenario, FAILURE_APPLIERS
from app.core.propagation import propagate_failures


if __name__ == "__main__":
    result = run_baseline_simulation()

    print("\n=== BASELINE ===")
    for svc in result.services.values():
        print(f"{svc.name:20} | {svc.status}")

    FAILURE_APPLIERS[FailureScenario.DATABASE_LATENCY_SPIKE](result)
    propagate_failures(result)

    print("\n=== AFTER DATABASE FAILURE ===")
    for svc in result.services.values():
        print(
            f"{svc.name:20} | "
            f"latency={svc.latency_ms:.1f}ms | "
            f"errors={svc.error_rate_pct:.2f}% | "
            f"status={svc.status}"
        )
