from app.core.simulation import run_baseline_simulation

if __name__ == "__main__":
    result = run_baseline_simulation()

    print("\n=== SERVICE STATES ===")
    for key, svc in result.services.items():
        print(
            f"{svc.name:20} | "
            f"latency={svc.latency_ms:.1f}ms | "
            f"errors={svc.error_rate_pct:.2f}% | "
            f"status={svc.status}"
        )

    print("\n=== METRICS SAMPLE ===")
    print("Latency:", result.metrics["latency_ms"][:5])
    print("Errors :", result.metrics["error_rate_pct"][:5])

## cd backend ,
##  python -m app.core.testrun_baseline