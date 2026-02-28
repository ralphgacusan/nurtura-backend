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
    Register a new user account.

    - Accepts a UserCreate schema with all required registration fields.
    - Returns the created user profile.
    - Raises an exception if the username or email already exists.
    """
    db_user = await user_service.register(user)
    return db_user


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
    Retrieve the profile of the currently authenticated user.

    - Returns a UserRead schema with user details.
    - Raises 404 if the user is not found (should not happen for an active token).
    """
    return await user_service.get_account(current_user.user_id)


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
    Update fields of the currently authenticated user's account.

    - Only fields provided in the request will be updated.
    - Returns the updated UserRead schema.
    - Raises an exception if username or email conflicts with another account.
    """
    return await user_service.update_account(current_user.user_id, updates)


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
    Change the password for the currently authenticated user.

    - Verifies the current password before applying the new password.
    - Returns confirmation upon success.
    - Raises an exception if current password is invalid.
    """
    return await user_service.change_password(current_user.user_id, payload)


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
    Permanently delete the currently authenticated user's account.

    - Returns a confirmation message upon successful deletion.
    - Raises an exception if the user cannot be deleted.
    """
    return await user_service.delete_account(current_user.user_id)