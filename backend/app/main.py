# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.simulate import router as simulate_router
from app.api.inject_failure import router as inject_failure_router
from app.api.scenarios import router as scenarios_router
from app.api.explain import router as explain_router


# Fast api
app = FastAPI(title="System Autopsy")

# -----------------------------
# CORS CONFIGURATION (REQUIRED)
# -----------------------------
# Allows the frontend (Vite on localhost:3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Register API routers
# -----------------------------
app.include_router(simulate_router)
app.include_router(inject_failure_router)
app.include_router(scenarios_router)
app.include_router(explain_router)


# -----------------------------
# Health check
# -----------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}
