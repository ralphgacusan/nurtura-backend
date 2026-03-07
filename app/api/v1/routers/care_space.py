# routers/care_space.py

"""
This module defines CareSpace management routes for the FastAPI application.

Handles:
- Creating, reading, updating, and deleting care spaces
- Listing members and dependents
- Generating join codes for care spaces
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated  # For type annotations with FastAPI dependencies

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import APIRouter, Depends  # APIRouter for route grouping, Depends for dependency injection

# ---------------------------
# Local Application Imports
# ---------------------------
from app.schemas import CareSpaceCreate, CareSpaceUpdate, CareSpaceRead, CareSpaceJoinCodeCreate
from app.services import CareSpaceService, CareSpaceJoinCodeService
from app.dependencies.care_space import get_care_space_service, get_care_space_join_code_service
from app.dependencies.auth import get_current_active_user, get_current_user  # Auth dependencies
from app.models.user import User  # User model for type hinting current_user

# ---------------------------
# Router Configuration
# ---------------------------
router = APIRouter(
    tags=["care_spaces"],  # Group all care space routes under this tag in Swagger UI
)

# ---------------------------
# Create Care Space
# ---------------------------
@router.post(
    "/",
    response_model=CareSpaceRead,
    description="Create a new care space (family members only)."
)
async def create_care_space(
    data: CareSpaceCreate,  # Schema containing care space details
    current_user: Annotated[User, Depends(get_current_user)],  # Ensure the requester is a family member
    service: Annotated[CareSpaceService, Depends(get_care_space_service)],  # Service layer
):
    """
    Create a new care space.

    Only users who are family members can perform this action.

    Parameters:
    - data: CareSpaceCreate object with care space details
    - current_user: Authenticated user making the request
    - service: CareSpaceService instance

    Returns:
    - CareSpaceRead: Details of the newly created care space
    """
    return await service.create_care_space(data, current_user)

# ---------------------------
# Generate Join Code
# ---------------------------
@router.post(
    "/{care_space_id}/generate-code",
    description="Generate a join code for a care space (owner only)."
)
async def generate_join_code(
    data: CareSpaceJoinCodeCreate,  # Schema containing care_space_id and optional default role
    current_user: Annotated[User, Depends(get_current_active_user)],  # Ensure requester is authenticated
    join_code_service: Annotated[CareSpaceJoinCodeService, Depends(get_care_space_join_code_service)],  # Service for join codes
):
    """
    Generate a join code for a care space.

    Only the owner of the care space can perform this action.

    Parameters:
    - data: CareSpaceJoinCodeCreate object with care_space_id and optional role
    - current_user: Authenticated user making the request
    - join_code_service: CareSpaceJoinCodeService instance

    Returns:
    - dict: Newly generated join code details
    """
    join_code_data = CareSpaceJoinCodeCreate(
        care_space_id=data.care_space_id,
        default_role="viewer"
    )
    return await join_code_service.generate_join_code(
        data=join_code_data, current_user=current_user
    )

# ---------------------------
# List Care Spaces for Current Member
# ---------------------------
@router.get(
    "/my-care-spaces",
    response_model=list[CareSpaceRead],
    description="List all care spaces where the current user is a member."
)
async def list_care_spaces_for_member(
    current_user: Annotated[User, Depends(get_current_active_user)],  # Authenticated user
    service: Annotated[CareSpaceService, Depends(get_care_space_service)],  # Service layer
):
    """
    Retrieve all care spaces that the current user belongs to.

    Parameters:
    - current_user: Authenticated user making the request
    - service: CareSpaceService instance

    Returns:
    - list[CareSpaceRead]: List of care spaces the user is a member of
    """
    return await service.list_care_spaces_for_member(current_user)

# ---------------------------
# Get Care Space by ID
# ---------------------------
@router.get(
    "/{care_space_id}",
    response_model=CareSpaceRead,
    description="Retrieve a care space by its ID."
)
async def get_care_space(
    care_space_id: int,  # ID of the care space to retrieve
    current_user: Annotated[User, Depends(get_current_active_user)],  # Authenticated user
    service: Annotated[CareSpaceService, Depends(get_care_space_service)],  # Service layer
):
    """
    Retrieve a care space by its ID.

    Parameters:
    - care_space_id: ID of the care space
    - current_user: Authenticated user making the request
    - service: CareSpaceService instance

    Returns:
    - CareSpaceRead: Details of the requested care space
    """
    return await service.get_care_space(care_space_id, current_user)

# ---------------------------
# Update Care Space
# ---------------------------
@router.put(
    "/{care_space_id}",
    response_model=CareSpaceRead,
    description="Update a care space (owner only)."
)
async def update_care_space(
    care_space_id: int,  # ID of the care space to update
    updates: CareSpaceUpdate,  # Schema containing updated care space details
    current_user: Annotated[User, Depends(get_current_active_user)],  # Ensure requester is the owner
    service: Annotated[CareSpaceService, Depends(get_care_space_service)],  # Service layer
):
    """
    Update a care space. Only the owner can perform this action.

    Parameters:
    - care_space_id: ID of the care space to update
    - updates: CareSpaceUpdate object with updated details
    - current_user: Authenticated user making the request
    - service: CareSpaceService instance

    Returns:
    - CareSpaceRead: Details of the updated care space
    """
    return await service.update_care_space(care_space_id, updates, current_user)

# ---------------------------
# Delete Care Space
# ---------------------------
@router.delete(
    "/{care_space_id}",
    description="Delete a care space (owner only)."
)
async def delete_care_space(
    care_space_id: int,  # ID of the care space to delete
    current_user: Annotated[User, Depends(get_current_active_user)],  # Ensure requester is the owner
    service: Annotated[CareSpaceService, Depends(get_care_space_service)],  # Service layer
):
    """
    Delete a care space. Only the owner can perform this action.

    Parameters:
    - care_space_id: ID of the care space to delete
    - current_user: Authenticated user making the request
    - service: CareSpaceService instance

    Returns:
    - dict: Success message or relevant information
    """
    return await service.delete_care_space(care_space_id, current_user)