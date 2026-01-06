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
    return f"""
System mode: {summary['system_mode']}

Affected services:
{summary['affected_services']}

Primary factors:
{summary['factors']}

Suggested mitigations:
{summary['mitigations']}

Write a clear, human-readable explanation of what happened and why.
"""
