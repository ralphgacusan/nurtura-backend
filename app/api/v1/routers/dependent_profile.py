"""
routers/dependent_profile.py

This module defines the dependent profile management routes for the FastAPI application.
It handles:
- Creating a dependent profile
- Retrieving dependent profile info (single or all for current user)
- Updating dependent profile info
- Changing the password of the linked user
- Deleting a dependent profile

All routes operate on the currently authenticated caregiver.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import APIRouter, Depends

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
from app.dependencies.auth import get_current_active_user
from app.models.user import User

# ---------------------------
# Router Configuration
# ---------------------------
router = APIRouter(
    tags=["dependent_profiles"],
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
    dependent_profile_data: DependentProfileCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],
):
    """
    Create a new dependent profile.

    - Only caregivers can create dependent profiles.
    - Raises an exception if the user already has a dependent profile.
    - Returns the created dependent profile with linked user info.
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
    dependent_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],
):
    """
    Fetch a dependent profile by its ID.

    - Raises 404 if the dependent profile is not found.
    - Returns the dependent profile along with linked user information.
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
    current_user: Annotated[User, Depends(get_current_active_user)],
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],
):
    """
    Retrieve all dependent profiles created by the current authenticated caregiver.

    - Returns a list of dependent profiles.
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
    dependent_id: int,
    updates: DependentProfileUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],
):
    """
    Update the fields of a dependent profile.

    - Only fields provided in the request are updated.
    - Raises 404 if the dependent profile is not found.
    - Returns the updated dependent profile.
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
    dependent_id: int,
    payload: DependentPasswordChange,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],
):
    """
    Change the password of the dependent's linked user.

    - Only caregivers can perform this action.
    - Requires current password and new password.
    - Returns a confirmation or raises an exception if credentials are invalid.
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
    dependent_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    dependent_profile_service: Annotated[DependentProfileService, Depends(get_dependent_profile_service)],
):
    """
    Delete a dependent profile.

    - Only caregivers can perform deletion.
    - Raises 404 if the dependent profile is not found.
    - Returns a confirmation message upon successful deletion.
    """
    return await dependent_profile_service.delete_profile(
        dependent_id=dependent_id,
        current_user=current_user
    )