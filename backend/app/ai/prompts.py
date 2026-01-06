SYSTEM_PROMPT = """
You are an AI system that explains distributed system failures.

Rules:
- You do NOT detect failures.
- You do NOT decide system state.
- You only explain provided facts.
- Do NOT invent metrics or services.
- Do NOT mention tools, models, or yourself.

Explain clearly and concisely.
"""


def build_explanation_prompt(summary: dict) -> str:
    services_block = "\n".join(
        f"- {name}: latency={data['latency_ms']:.1f}ms, "
        f"errors={data['error_rate_pct']:.2f}%, "
        f"status={data['status']}"
        for name, data in summary["services"].items()
    )

    factors = summary.get("identified_factors", [])
    mitigations = summary.get("mitigations", [])

    return f"""
System mode: {summary['system_mode']}

Service metrics:
{services_block}

Identified contributing factors:
{', '.join(factors) if factors else 'None'}

Suggested mitigations:
{', '.join(mitigations) if mitigations else 'None'}

Write a clear, human-readable explanation of what happened and why.
"""
