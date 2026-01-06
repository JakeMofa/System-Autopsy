from pydantic import BaseModel
from typing import List


class MitigationSuggestion(BaseModel):
    action: str
    description: str


class ExplanationResponse(BaseModel):
    text: List[str]
    identified_factors: List[str]
    mitigation_suggestions: List[MitigationSuggestion]
