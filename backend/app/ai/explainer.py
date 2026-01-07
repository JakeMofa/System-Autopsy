# app/ai/explainer.py

import os
import json
import requests
from typing import Dict, Any, Optional

from app.ai.validation import validate_explanation

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


# -----------------------------
# Strict system prompt
# -----------------------------

SYSTEM_PROMPT = """
You are an AI system that explains distributed system failures.

You are given structured, deterministic system data.
You MUST follow these rules:

- Use ONLY the provided data.
- Do NOT speculate about causes not present.
- Do NOT invent infrastructure issues (CPU, disk, memory).
- Do NOT invent metrics or services.
- Do NOT suggest automated actions.
- Explanations are informational only.

You MUST return VALID JSON matching the exact schema provided.
No prose outside JSON.
"""


# -----------------------------
# Output schema (contract)
# -----------------------------

OUTPUT_SCHEMA = {
    "system_state_summary": "string",
    "failure_explanation": "string",
    "identified_factors": ["string"],
    "mitigation_suggestions": [
        {
            "title": "string",
            "description": "string"
        }
    ]
}


# -----------------------------
# Prompt builder
# -----------------------------

def build_structured_prompt(payload: Dict[str, Any]) -> str:
    """
    Build a strict, schema-enforced prompt for the LLM.
    """

    return f"""
You are given the following system state:

{json.dumps(payload, indent=2)}

Your task:
1. Summarize the overall system state.
2. Explain the failure using only the provided data.
3. List the identified contributing factors.
4. Provide mitigation suggestions (informational only).

Output MUST be valid JSON and match this schema exactly:

{json.dumps(OUTPUT_SCHEMA, indent=2)}
"""


# -----------------------------
# AI explanation entry point
# -----------------------------

def generate_ai_explanation(
    explain_payload: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Generate a structured AI explanation using Ollama (LLaMA).

    Returns:
        Dict with keys:
          - system_state_summary
          - failure_explanation
          - identified_factors
          - mitigation_suggestions

        OR None if generation or validation fails.
    """

    try:
        user_prompt = build_structured_prompt(explain_payload)
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
            },
            timeout=60,
        )

        if response.status_code != 200:
            print("OLLAMA ERROR:", response.text)
            return None

        data = response.json()
        raw_text = data.get("response", "").strip()

        if not raw_text:
            return None

        # -----------------------------
        # Parse JSON strictly
        # -----------------------------
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            print("AI returned non-JSON output")
            return None

        # -----------------------------
        # Minimal structural validation
        # -----------------------------
        required_keys = {
            "system_state_summary",
            "failure_explanation",
            "identified_factors",
            "mitigation_suggestions",
        }

        if not required_keys.issubset(parsed.keys()):
            print("AI output missing required fields")
            return None

        if not isinstance(parsed["identified_factors"], list):
            return None

        if not isinstance(parsed["mitigation_suggestions"], list):
            return None

        # Optional: validate text fields for hallucination signals
        if not validate_explanation(parsed["failure_explanation"]):
            return None

        return parsed

    except Exception as e:
        print("OLLAMA AI ERROR:", e)
        return None
