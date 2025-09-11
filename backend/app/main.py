# backend/app/main.py
"""
App entrypoint. Keep this file minimal: it boots FastAPI and mounts routers.
"""

from fastapi import FastAPI
from app.routes import upload, health  # import routers from app.routes package

app = FastAPI(
    title="AI PDF Analyzer",
    description="Backend for uploading and analyzing PDFs (refactored routing + services).",
    version="0.2.0"
)


@app.on_event("startup")
async def on_startup():
    """
    Save a startup timestamp in app.state for simple uptime checks.
    """
    import time
    app.state.start_time = time.time()


# Mount routers
# - health router will be available at /health
# - upload router will be available under /api (e.g. POST /api/upload-pdf)
app.include_router(health.router, prefix="", tags=["Health"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
