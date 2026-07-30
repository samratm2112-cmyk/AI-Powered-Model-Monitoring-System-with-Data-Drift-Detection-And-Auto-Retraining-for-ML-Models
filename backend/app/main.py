"""
🚀 FASTAPI BACKEND MAIN APPLICATION
Entry point for FastAPI service layer. Configures CORS, mounts endpoints, and sets up OpenAPI docs.
"""

import sys
import os

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import PROJECT_NAME, PROJECT_VERSION
from backend.app.api.endpoints import router as api_router

app = FastAPI(
    title=PROJECT_NAME,
    description="Production REST API service layer for ML Continuous Drift Detection & Monitoring System.",
    version=PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware for future React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Endpoints Router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
