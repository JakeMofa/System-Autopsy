from fastapi import APIRouter
from app.core.failures import FailureScenario

router = APIRouter()


@router.get("/scenarios")
def list_scenarios():
    return {
        "scenarios": [scenario.value for scenario in FailureScenario]
    }
