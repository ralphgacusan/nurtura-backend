"""
main.py

Entry point for the Nurtura API FastAPI application.

Features:
- Initializes FastAPI instance
- Includes API routers with dynamic prefixes
- Provides optional health check endpoint
"""

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import FastAPI  # core FastAPI class to create the app instance

# ---------------------------
# Local App Imports
# ---------------------------
from app.api.v1.routers.auth import router as auth_router  # auth routes (login, refresh, logout)
from app.api.v1.routers.user import router as user_router  # user management routes (register, profile)
from app.core.config import settings  # project configuration, including API prefix

# ---------------------------
# API Configuration
# ---------------------------
api_prefix = settings.API_PREFIX  # dynamic prefix (e.g., "/api/v1") from config

# Initialize FastAPI app instance
app = FastAPI(
    title="Nurtura API",
    description=(
        "Backend API for Nurtura, a caregiving coordination platform. "
        "Provides modules for caregiver and dependent management, task scheduling, "
        "notifications, collaborative care spaces, dashboards, and AI-assisted support."
    ),
    version="1.0.0",
)

# ---------------------------
# Include Routers
# ---------------------------
# Authentication routes (login, token, logout)
app.include_router(auth_router, prefix=f"{api_prefix}/auth")

# User management routes (register, profile, update, delete)
app.include_router(user_router, prefix=f"{api_prefix}/users")

# ---------------------------
# Health Check / Test Endpoint
# ---------------------------
@app.get(f"{api_prefix}/ping", tags=["health"])
async def ping():
    """
    Simple endpoint to verify that the API is running.
    Returns a static response {"ping": "pong"} for monitoring.
    """
    return {"ping": "pong"}