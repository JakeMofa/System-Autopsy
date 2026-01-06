from fastapi import FastAPI

from app.api.simulate import router as simulate_router
from app.api.inject_failure import router as inject_failure_router
from app.api.scenarios import router as scenarios_router
from app.api.explain import router as explain_router


app = FastAPI(title="System Autopsy")

# Register API routers
app.include_router(simulate_router)
app.include_router(inject_failure_router)
app.include_router(scenarios_router)
app.include_router(explain_router)



@app.get("/health")
def health_check():
    return {"status": "ok"}
