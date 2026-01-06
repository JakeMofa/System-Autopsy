import subprocess
import json

from app.ai.prompts import SYSTEM_PROMPT, build_explanation_prompt
from app.ai.validation import validate_explanation


OLLAMA_MODEL = "mistral"


def generate_ai_explanation(summary: dict) -> str | None:
    """
    Generate an AI explanation using Ollama.
    Returns None if AI fails or output is invalid.
    """

    try:
        prompt = build_explanation_prompt(summary)

        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode != 0:
            return None

        ai_text = result.stdout.strip()

        if not ai_text:
            return None

        if not validate_explanation(ai_text):
            return None

        return ai_text

    except Exception:
        return None
