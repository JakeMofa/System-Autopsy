from app.ai.prompts import SYSTEM_PROMPT, build_explanation_prompt
from app.ai.validation import validate_explanation


def generate_ai_explanation(summary: dict) -> str | None:
    """
    Optional AI explanation.
    Return None if AI fails or output is invalid.
    """

    try:
        #  Placeholder for now (no dependency required)
        # Later  i will plug in Ollama / OpenAI here

        prompt = build_explanation_prompt(summary)

        # TEMP: simulated AI response
        ai_text = (
            "The system experienced degradation due to increased database latency, "
            "which caused downstream services to slow as requests queued and retries increased."
        )

        if not validate_explanation(ai_text):
            return None

        return ai_text

    except Exception:
        return None
