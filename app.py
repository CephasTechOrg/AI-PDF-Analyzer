# backend/app/main.py
"""
FastAPI entrypoint for AI PDF Analyzer backend.

This file:
- Creates the FastAPI app
- Saves a startup timestamp (used by health endpoint uptime)
- Includes routers from the `api` package
"""

import time
from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.upload import router as upload_router

app = FastAPI(
    title="AI PDF Analyzer - Backend",
    version="0.1.0",
    description="Backend skeleton for uploading PDFs and querying them."
)

# Store process start time in app.state so endpoints (health) can compute uptime.
# Why: gives a simple liveness/readiness metric without external monitoring.
@app.on_event("startup")
async def startup_event():
    app.state.start_time = time.time()

# Mount routers. We use routers to keep the code modular as project grows.
app.include_router(health_router, prefix="")
app.include_router(upload_router, prefix="/api")

# Example: uvicorn app.main:app --reload --port 8000
