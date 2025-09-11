# backend/app/routes/health.py
"""
Health-check endpoints. Lightweight and safe for frequent probes.
"""

from fastapi import APIRouter, Request
import time

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    """
    Returns status and uptime in seconds.
    Uses request.app.state.start_time (set at startup in main.py).
    """
    start = getattr(request.app.state, "start_time", None)
    uptime = time.time() - start if start else 0.0
    return {"status": "ok", "uptime_seconds": round(uptime, 2)}
