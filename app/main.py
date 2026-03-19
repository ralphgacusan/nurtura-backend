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
from app.api.v1.routers.task import router as task_router
from app.api.v1.routers.chatbot import router as chatbot_router
from app.api.v1.routers.dashboard import router as dashboard_router


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

# Tasks
app.include_router(
    task_router,
    prefix=f"{api_prefix}/tasks",
    tags=["tasks"]
)


# Chatbot
app.include_router(
    dashboard_router,
    prefix=f"{api_prefix}/dashboard",
    tags=["dashboard"]
)


# Chatbot
app.include_router(
    chatbot_router,
    prefix=f"{api_prefix}/chatbot",
    tags=["chatbot"]
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


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
