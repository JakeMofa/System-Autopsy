import os
import requests

from app.ai.prompts import SYSTEM_PROMPT, build_explanation_prompt
from app.ai.validation import validate_explanation

#  PLACEHOLDER — you will paste your real key here or via env
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "PASTE_YOUR_GROQ_API_KEY_HERE")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"


def generate_groq_explanation(summary: dict) -> str | None:
    try:
        prompt = build_explanation_prompt(summary)

        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
            },
            timeout=15,
        )

        if response.status_code != 200:
            return None

        data = response.json()
        ai_text = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not ai_text:
            return None

        if not validate_explanation(ai_text):
            return None

        return ai_text

    except Exception as e:
        print("GROQ AI ERROR:", e)
        return None
