"""
routers/dependent_profile.py

This module defines the dependent profile management routes for the FastAPI application.

Handles:
- Creating a dependent profile
- Retrieving dependent profile info (single or all for current user)
- Updating dependent profile info
- Changing the password of the linked user
- Deleting a dependent profile

All routes operate on the currently authenticated family member.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated  # For type annotations with FastAPI dependencies

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import APIRouter, Depends  # APIRouter for grouping routes, Depends for DI

# ---------------------------
# Local Application Imports
# ---------------------------
from app.schemas.dependent_profile import (
    DependentPasswordChange,
    DependentProfileCreate,
    DependentProfileUpdate,
    DependentProfileRead
)
from app.services.dependent_profile import DependentProfileService
from app.dependencies.dependent_profile import get_dependent_profile_service
from app.dependencies.auth import get_current_active_user  # Auth dependency to get current user
from app.models.user import User  # User model for type hinting

# ---------------------------
# Router Configuration
# ---------------------------
router = APIRouter(
    tags=["dependent_profiles"],  # Group all dependent profile routes under this tag
)

# ---------------------------
# Create Dependent Profile
# ---------------------------
@router.post(
    "/register",
    response_model=DependentProfileRead,
    description="Create a new dependent profile linked to a user."
)
async def create_dependent_profile(
    dependent_profile_data: DependentProfileCreate,  # Input data for creating dependent
    current_user: Annotated[User, Depends(get_current_active_user)],  # Authenticated user creating the dependent
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],  # Service layer
):
    """
    Create a new dependent profile.

    - Only family members can create dependent profiles.
    - Raises an exception if the user already has a dependent profile.
    - Returns the created dependent profile along with linked user info.

    Parameters:
    - dependent_profile_data: DependentProfileCreate schema
    - current_user: Authenticated user performing the action
    - dependent_profile_service: DependentProfileService instance

    Returns:
    - DependentProfileRead: Created dependent profile details
    """
    return await dependent_profile_service.create_profile(
        dependent_profile_data=dependent_profile_data,
        created_by=current_user.user_id,
        current_user=current_user
    )

# ---------------------------
# Get Dependent Profile by ID
# ---------------------------
@router.get(
    "/{dependent_id}",
    response_model=DependentProfileRead,
    description="Retrieve a dependent profile by its ID."
)
async def get_dependent_profile(
    dependent_id: int,  # ID of the dependent profile to retrieve
    current_user: Annotated[User, Depends(get_current_active_user)],  # Authenticated user
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],
):
    """
    Fetch a dependent profile by its ID.

    - Raises 404 if the dependent profile is not found.
    - Returns the dependent profile along with linked user information.

    Parameters:
    - dependent_id: ID of the dependent profile
    - current_user: Authenticated user performing the request
    - dependent_profile_service: DependentProfileService instance

    Returns:
    - DependentProfileRead: Retrieved dependent profile
    """
    return await dependent_profile_service.get_profile(
        dependent_id=dependent_id,
        current_user=current_user
    )

# ---------------------------
# Get all dependents for current user
# ---------------------------
@router.get(
    "/me/dependents",
    response_model=list[DependentProfileRead],
    description="Get all dependent profiles created by the current user."
)
async def get_my_dependents(
    current_user: Annotated[User, Depends(get_current_active_user)],  # Authenticated user
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],
):
    """
    Retrieve all dependent profiles created by the current authenticated family member.

    - Returns a list of dependent profiles.

    Parameters:
    - current_user: Authenticated user
    - dependent_profile_service: DependentProfileService instance

    Returns:
    - list[DependentProfileRead]: List of dependent profiles for the user
    """
    return await dependent_profile_service.get_dependents_for_user(
        current_user=current_user
    )

# ---------------------------
# Update Dependent Profile
# ---------------------------
@router.put(
    "/{dependent_id}",
    response_model=DependentProfileRead,
    description="Update a dependent profile's information."
)
async def update_dependent_profile(
    dependent_id: int,  # ID of the dependent profile to update
    updates: DependentProfileUpdate,  # Fields to update
    current_user: Annotated[User, Depends(get_current_active_user)],  # Authenticated user
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],
):
    """
    Update the fields of a dependent profile.

    - Only fields provided in the request are updated.
    - Raises 404 if the dependent profile is not found.
    - Returns the updated dependent profile.

    Parameters:
    - dependent_id: ID of the dependent profile
    - updates: DependentProfileUpdate schema
    - current_user: Authenticated user performing the update
    - dependent_profile_service: DependentProfileService instance

    Returns:
    - DependentProfileRead: Updated dependent profile
    """
    return await dependent_profile_service.update_profile(
        dependent_id=dependent_id,
        updates=updates,
        current_user=current_user
    )

# ---------------------------
# Change Password for Dependent's User
# ---------------------------
@router.put(
    "/{dependent_id}/change-password",
    description="Change the password of the user linked to this dependent profile."
)
async def change_dependent_profile_password(
    dependent_id: int,  # ID of the dependent profile
    payload: DependentPasswordChange,  # Current and new password info
    current_user: Annotated[User, Depends(get_current_active_user)],  # Authenticated user
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],
):
    """
    Change the password of the dependent's linked user.

    - Only family members can perform this action.
    - Requires current password and new password.
    - Returns a confirmation or raises an exception if credentials are invalid.

    Parameters:
    - dependent_id: ID of the dependent profile
    - payload: DependentPasswordChange schema with current and new password
    - current_user: Authenticated user performing the change
    - dependent_profile_service: DependentProfileService instance

    Returns:
    - dict: Confirmation message
    """
    return await dependent_profile_service.change_password(
        dependent_id=dependent_id,
        payload=payload,
        current_user=current_user
    )

# ---------------------------
# Delete Dependent Profile
# ---------------------------
@router.delete(
    "/{dependent_id}",
    description="Delete a dependent profile by its ID."
)
async def delete_dependent_profile(
    dependent_id: int,  # ID of the dependent profile to delete
    current_user: Annotated[User, Depends(get_current_active_user)],  # Authenticated user
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],
):
    """
    Delete a dependent profile.

    - Only family members can perform deletion.
    - Raises 404 if the dependent profile is not found.
    - Returns a confirmation message upon successful deletion.

    Parameters:
    - dependent_id: ID of the dependent profile
    - current_user: Authenticated user performing the deletion
    - dependent_profile_service: DependentProfileService instance

    Returns:
    - dict: Confirmation message
    """
    return await dependent_profile_service.delete_profile(
        dependent_id=dependent_id,
        current_user=current_user
    )