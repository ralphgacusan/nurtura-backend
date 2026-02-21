"""
routers/user.py

This module defines the user management routes for the FastAPI application.
It handles:
- User registration
- Retrieving current user info
- Updating user info
- Changing password
- Deleting own account

All routes operate on the currently authenticated user where applicable.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated  # For type hints with FastAPI Depends

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import APIRouter, Depends  # Router and dependency injection

# ---------------------------
# Local Application Imports
# ---------------------------
from app.schemas.user import PasswordChange, UserRead, UserUpdate, UserCreate  # User input/output schemas
from app.services.user import UserService  # Business logic service for users
from app.dependencies.user import get_user_service  # Dependency injection for UserService
from app.dependencies.auth import get_current_active_user  # Get current active user from token
from app.models.user import User  # ORM model

# ---------------------------
# Router Configuration
# ---------------------------
router = APIRouter(
    tags=["users"],   # Swagger tag
)

# ---------------------------
# User Registration
# ---------------------------
@router.post(
    "/register",
    response_model=UserRead,
    description="Register a new user in the system."
)
async def register(
    user: UserCreate,  # Input schema for new user
    user_service: Annotated[UserService, Depends(get_user_service)],  # Inject UserService
):
    """
    Handle user registration.
    """
    db_user = await user_service.register(user)  # Call service to create user
    return db_user  # Return newly created user


# ---------------------------
# Get Current User Info
# ---------------------------
@router.get(
    "/me",
    response_model=UserRead,
    description="Retrieve information about the currently authenticated user."
)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)],  # Authenticated user from token
    user_service: Annotated[UserService, Depends(get_user_service)],  # Inject UserService
):
    """
    Return current user's profile.
    """
    return await user_service.get_account(current_user.user_id)  # Fetch user info


# ---------------------------
# Update Current User Info
# ---------------------------
@router.put(
    "/me",
    response_model=UserRead,
    description="Update the profile information of the current user."
)
async def update_current_user(
    updates: UserUpdate,  # Fields to update
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    Update user account with provided fields.
    """
    return await user_service.update_account(current_user.user_id, updates)  # Update via service


# ---------------------------
# Change Password
# ---------------------------
@router.put(
    "/me/password",
    description="Change the password of the currently authenticated user."
)
async def change_password(
    payload: PasswordChange,  # Contains current and new password
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    Update user's password after verifying current password.
    """
    await user_service.change_password(current_user.user_id, payload)  # Delegate to service
    return {"detail": "Password updated successfully."}  # Success message


# ---------------------------
# Delete Current User Account
# ---------------------------
@router.delete(
    "/me",
    description="Delete the currently authenticated user's account."
)
async def delete_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    Delete user account permanently.
    """
    await user_service.delete_account(current_user.user_id)  # Delete via service
    return {"detail": "Your account has been deleted successfully."}  # Confirmation message