"""
main.py

Entry point for the Nurtura API FastAPI application.

Features:
- Initializes FastAPI instance
- Includes API routers with dynamic prefixes
- Provides health check endpoint
- Integrates Care Space, Dependent, and User modules
"""

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import FastAPI

# ---------------------------
# Local App Imports
# ---------------------------
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.user import router as user_router
from app.api.v1.routers.dependent_profile import router as dependent_profile_router
from app.api.v1.routers.care_space import router as care_space_router
from app.api.v1.routers.care_space_member import router as care_space_member_router
from app.core.config import settings

# ---------------------------
# API Configuration
# ---------------------------
api_prefix = settings.API_PREFIX  # e.g., "/api/v1"

# ---------------------------
# Initialize FastAPI App
# ---------------------------
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
# Authentication
app.include_router(auth_router, prefix=f"{api_prefix}/auth", tags=["auth"])

# Users
app.include_router(user_router, prefix=f"{api_prefix}/users", tags=["users"])

# Dependent Profiles
app.include_router(
    dependent_profile_router,
    prefix=f"{api_prefix}/dependent-profiles",
    tags=["dependent_profiles"]
)

# Care Spaces
app.include_router(care_space_router, prefix=f"{api_prefix}/care-spaces", tags=["care_spaces"])

# Care Space Members
app.include_router(
    care_space_member_router,
    prefix=f"{api_prefix}/care-space-members",
    tags=["care_space_members"]
)

# ---------------------------
# Health Check Endpoint
# ---------------------------
@app.get(f"{api_prefix}/ping", tags=["health"])
async def ping():
    """
    Simple endpoint to verify that the API is running.
    Returns:
        dict: {"ping": "pong"}
    """
    return {"ping": "pong"}