"""
services/care_space_member_service.py

Service layer for managing CareSpace members.

Responsibilities:
- Add, update, and remove members from a care space
- Validate permissions: only family owners can modify members
- List members of a care space
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime

# ---------------------------
# Local App Imports
# ---------------------------
from app.repositories.care_space_member import CareSpaceMemberRepository
from app.repositories.care_space import CareSpaceRepository
from app.repositories.user import UserRepository
from app.schemas.care_space_member import CareSpaceMemberCreate, CareSpaceMemberUpdate, CareSpaceMemberRead
from app.models.user import User
from app.core.permissions import ensure_member, ensure_family_owner
from app.core.exceptions import care_space_not_found_exception, user_not_found_exception

# ---------------------------
# CareSpaceMember Service
# ---------------------------
class CareSpaceMemberService:
    """
    Service for managing CareSpaceMember operations.

    Permissions:
        Only family owners can add, update, or remove members.
    """

    def __init__(
        self,
        member_repo: CareSpaceMemberRepository,
        care_space_repo: CareSpaceRepository,
        user_repo: UserRepository
    ):
        """Initialize service with required repositories."""
        self.member_repo = member_repo
        self.care_space_repo = care_space_repo
        self.user_repo = user_repo

    # ---------------------------
    # PRIVATE METHOD: GET MEMBER
    # ---------------------------
    async def _get_member(self, care_space_id: int, user: User):
        """
        Retrieve the current user's membership in a care space.

        Args:
            care_space_id (int): ID of the care space
            user (User): Current authenticated user

        Raises:
            care_space_member_not_found_exception: If user is not a member

        Returns:
            CareSpaceMember: Membership object
        """
        member = await self.member_repo.get_member(care_space_id, user.user_id)
        ensure_member(member)
        return member

    # ---------------------------
    # ADD MEMBER
    # ---------------------------
    async def add_member(self, data: CareSpaceMemberCreate, current_user: User) -> CareSpaceMemberRead:
        """
        Add a new member to a care space.

        Only family owners can add members.

        Args:
            data (CareSpaceMemberCreate): Data of the member to add
            current_user (User): Authenticated user performing the action

        Returns:
            CareSpaceMemberRead: Created membership info
        """
        # Ensure current user is a member and has owner privileges
        member = await self._get_member(data.care_space_id, current_user)
        ensure_family_owner(member, current_user)

        # Validate care space exists
        care_space = await self.care_space_repo.get_by_id(data.care_space_id)
        if not care_space:
            raise care_space_not_found_exception
        
        # Validate user exists
        user_to_add = await self.user_repo.get_by_id(data.user_id)
        if not user_to_add:
            raise user_not_found_exception 

        # Prepare member data and add to DB
        member_data = CareSpaceMemberCreate(
            care_space_id=care_space.care_space_id,
            user_id=data.user_id,
            role_in_space=data.role_in_space
        )
        new_member = await self.member_repo.add_member(member_data)
        await self.member_repo.db.commit()

        # Reload member with user info
        new_member = await self.member_repo.get_by_id(new_member.member_id, eager_load_user=True)
        return CareSpaceMemberRead.model_validate(new_member)

    # ---------------------------
    # UPDATE MEMBER
    # ---------------------------
    async def update_member(self, member_id: int, updates: CareSpaceMemberUpdate, current_user: User) -> CareSpaceMemberRead:
        """
        Update a member record (role or left_at).

        Only family owners can update member roles.

        Args:
            member_id (int): ID of the member to update
            updates (CareSpaceMemberUpdate): Updated fields
            current_user (User): Authenticated user performing the action

        Returns:
            CareSpaceMemberRead: Updated membership info
        """
        # Fetch member and validate permissions
        member = await self.member_repo.get_by_id(member_id, eager_load_user=True)
        checked_member = await self._get_member(member.care_space_id, current_user)
        ensure_family_owner(checked_member, current_user)

        # Update member record
        updated_member = await self.member_repo.update_member(member_id, updates)

        # Reload with eager loading to avoid missing related user data
        updated_member = await self.member_repo.get_by_id(updated_member.member_id, eager_load_user=True)
        return CareSpaceMemberRead.model_validate(updated_member)

    # ---------------------------
    # REMOVE MEMBER
    # ---------------------------
    async def remove_member(self, member_id: int, current_user: User):
        """
        Remove a member from a care space.

        Only family owners can remove members.

        Args:
            member_id (int): ID of the member to remove
            current_user (User): Authenticated user performing the action

        Returns:
            dict: Confirmation message
        """
        member = await self.member_repo.get_by_id(member_id, eager_load_user=True)
        checked_member = await self._get_member(member.care_space_id, current_user)
        ensure_family_owner(checked_member, current_user)

        await self.member_repo.remove_member(member)
        return {"detail": "Member removed successfully"}

    # ---------------------------
    # LIST MEMBERS
    # ---------------------------
    async def list_members(self, care_space_id: int, current_user: User):
        """
        List all members of a care space.

        Args:
            care_space_id (int): Care space ID
            current_user (User): Authenticated user performing the action

        Returns:
            list[CareSpaceMemberRead]: List of members with nested user info
        """
        # Ensure current user is a member
        await self._get_member(care_space_id, current_user)

        # Fetch members
        members = await self.member_repo.list_members(care_space_id, eager_load_user=True)
        return [CareSpaceMemberRead.model_validate(member) for member in members]
    
    # ---------------------------
    # ENSURE USER IS MEMBER (PUBLIC)
    # ---------------------------
    async def ensure_user_is_member(self, care_space_id: int, user_id: int):
        """
        Ensure that a user is a member of a care space.

        Used by other services (TaskService, ScheduleService, etc.)

        Args:
            care_space_id (int)
            user_id (int)

        Raises:
            forbidden_exception if not member
        """

        member = await self.member_repo.get_member(
            care_space_id,
            user_id
        )

        ensure_member(member)

        return member