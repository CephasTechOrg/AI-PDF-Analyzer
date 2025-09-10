# backend/app/api/health.py
"""
Health-check endpoints.

Provides:
- GET /health  -> simple liveness + lightweight readiness info (uptime + quick checks)
- GET /ready   -> (optional) more detailed readiness checks (DB, vector DB, cache).
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
import time
import shutil
import os

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    checks: dict

def check_disk_space(threshold_mb=100):
    """
    Simple disk-space check for readiness.
    Returns ('ok'|'low') and free MB.
    Why: if disk is full, indexing/upload will fail; it's useful for deployments.
    """
    total, used, free = shutil.disk_usage(".")
    free_mb = free // (1024 * 1024)
    status = "ok" if free_mb >= threshold_mb else "low"
    return {"status": status, "free_mb": free_mb}

@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health(request: Request):
    """
    Lightweight health endpoint.
    - Returns "ok" if process is alive.
    - Returns uptime_seconds computed from startup time.
    - Includes a small set of local checks (disk space).
    Expand this later with DB/cache checks as needed.
    """
    # Calculate uptime using the startup timestamp saved in app.state
    start = getattr(request.app.state, "start_time", None)
    uptime = time.time() - start if start else 0.0

    # Basic checks (fast, won't block)
    disk = check_disk_space()
    # Example additional checks you can add later:
    # - database reachable?
    # - vector DB accessible?
    # - 3rd-party API reachable (DeepSeek auth check)
    checks = {
        "disk_space": disk,
        # placeholder entries (not implemented yet)
        "db": {"status": "not-configured"},
        "vector_db": {"status": "not-configured"},
        "external_api_deepseek": {"status": "not-configured"},
    }

    return HealthResponse(status="ok", uptime_seconds=round(uptime, 2), checks=checks)
