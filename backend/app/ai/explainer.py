import os
import requests

from app.ai.prompts import SYSTEM_PROMPT, build_explanation_prompt
from app.ai.validation import validate_explanation

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


def generate_ai_explanation(summary: dict) -> str | None:
    """
    Generate an AI explanation using Ollama (HTTP API).
    Returns None if AI fails or output is invalid.
    """

    try:
        prompt = build_explanation_prompt(summary)
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

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
            return None

        data = response.json()
        ai_text = data.get("response", "").strip()

        if not ai_text:
            return None

        if not validate_explanation(ai_text):
            return None

        return ai_text

    except Exception as e:
        print("OLLAMA AI ERROR:", e)
        return None
