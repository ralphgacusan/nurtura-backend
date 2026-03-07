# routers/care_space_member.py

"""
CareSpaceMember routes for FastAPI.

Handles:
- Adding members to a care space
- Updating member roles or status
- Removing members
- Listing all members of a care space
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
from app.schemas.care_space_member import CareSpaceMemberCreate, CareSpaceMemberUpdate, CareSpaceMemberRead
from app.services.care_space_member import CareSpaceMemberService
from app.dependencies.care_space_member import get_care_space_member_service
from app.dependencies.auth import get_current_active_user  # Dependency to get the currently authenticated user
from app.models.user import User  # User model for type hinting current_user

# ---------------------------
# Router Configuration
# ---------------------------
router = APIRouter(
    tags=["care_space_members"],  # Group all care space member routes under this tag in Swagger UI
)

# ---------------------------
# Add Member
# ---------------------------
@router.post(
    "/",
    response_model=CareSpaceMemberRead,
    description="Add a member to a care space (owner only)."
)
async def add_member(
    data: CareSpaceMemberCreate,  # Schema containing user_id and role
    current_user: Annotated[User, Depends(get_current_active_user)],  # Ensure the requester is authenticated
    service: Annotated[CareSpaceMemberService, Depends(get_care_space_member_service)],  # Service layer
):
    """
    Add a user as a member to a care space.
    Only the care space owner can perform this action.

    Parameters:
    - data: CareSpaceMemberCreate object with member details
    - current_user: The authenticated user making the request
    - service: CareSpaceMemberService instance

    Returns:
    - CareSpaceMemberRead: Details of the newly added member
    """
    return await service.add_member(data, current_user)

# ---------------------------
# Update Member
# ---------------------------
@router.put(
    "/{member_id}",
    response_model=CareSpaceMemberRead,
    description="Update a member's role or status (owner only)."
)
async def update_member(
    member_id: int,  # ID of the member to update
    updates: CareSpaceMemberUpdate,  # Schema containing updated role or status
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: Annotated[CareSpaceMemberService, Depends(get_care_space_member_service)],
):
    """
    Update a member's role or status within a care space.
    Only the care space owner can perform this action.

    Parameters:
    - member_id: ID of the member to update
    - updates: CareSpaceMemberUpdate object with new role/status
    - current_user: Authenticated user making the request
    - service: CareSpaceMemberService instance

    Returns:
    - CareSpaceMemberRead: Details of the updated member
    """
    return await service.update_member(member_id, updates, current_user)

# ---------------------------
# Remove Member
# ---------------------------
@router.delete(
    "/{member_id}",
    description="Remove a member from a care space (owner only)."
)
async def remove_member(
    member_id: int,  # ID of the member to remove
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: Annotated[CareSpaceMemberService, Depends(get_care_space_member_service)],
):
    """
    Remove a member from a care space.
    Only the care space owner can perform this action.

    Parameters:
    - member_id: ID of the member to remove
    - current_user: Authenticated user making the request
    - service: CareSpaceMemberService instance

    Returns:
    - dict: Success message or relevant information
    """
    return await service.remove_member(member_id, current_user)

# ---------------------------
# List Members of a Care Space
# ---------------------------
@router.get(
    "/care-space/{care_space_id}",
    response_model=list[CareSpaceMemberRead],
    description="List all members of a care space."
)
async def list_members(
    care_space_id: int,  # ID of the care space
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: Annotated[CareSpaceMemberService, Depends(get_care_space_member_service)],
):
    """
    Retrieve a list of all members in a care space.

    Parameters:
    - care_space_id: ID of the care space
    - current_user: Authenticated user making the request
    - service: CareSpaceMemberService instance

    Returns:
    - list[CareSpaceMemberRead]: List of all care space members
    """
    return await service.list_members(care_space_id, current_user)