from fastapi import FastAPI

from app.api.simulate import router as simulate_router
from app.api.inject_failure import router as inject_failure_router

app = FastAPI(title="System Autopsy")

# Register API routers
app.include_router(simulate_router)
app.include_router(inject_failure_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
