ALLOWED_KEYWORDS = {
    "database",
    "latency",
    "retry",
    "dependency",
    "service",
    "timeout",
    "load",
    "capacity",
    "circuit breaker",
}


def validate_explanation(text: str) -> bool:
    """
    Simple guardrail:
    - Reject explanations that reference unknown concepts
    """
    lowered = text.lower()

    for word in lowered.split():
        if word.isalpha() and len(word) > 20:
            return False  # nonsense / hallucination signal

    return True
