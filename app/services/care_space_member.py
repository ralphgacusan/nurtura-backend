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
from app.schemas.care_space_member import CareSpaceMemberCreate, CareSpaceMemberUpdate, CareSpaceMemberRead, CareSpaceMemberBulkCreate
from app.models.user import User
from app.core.permissions import ensure_member, ensure_family_owner
from app.core.exceptions import care_space_not_found_exception, user_not_found_exception
from app.services.notification import NotificationService
from app.schemas.notification import NotificationCreate
from fastapi import HTTPException
from app.core.exceptions import care_space_member_not_found_exception
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
        user_repo: UserRepository,
        notification_service: NotificationService

    ):
        """Initialize service with required repositories."""
        self.member_repo = member_repo
        self.care_space_repo = care_space_repo
        self.user_repo = user_repo
        self.notification_service = notification_service


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
    async def add_members(
        self,
        data: CareSpaceMemberBulkCreate,
        current_user: User
    ) -> list[CareSpaceMemberRead]:

        # Validate owner
        member = await self._get_member(data.care_space_id, current_user)
        ensure_family_owner(member, current_user)

        # Validate care space
        care_space = await self.care_space_repo.get_by_id(data.care_space_id)
        if not care_space:
            raise care_space_not_found_exception

        created_members = []

        for user_id in data.user_ids:

            # Validate user
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise user_not_found_exception

            # Skip if already member (optional but recommended)
            existing = await self.member_repo.get_member(
                data.care_space_id,
                user_id
            )
            if existing:
                continue  # or raise exception

            member_data = CareSpaceMemberCreate(
                care_space_id=data.care_space_id,
                user_id=user_id,
                role_in_space="viewer"
            )

            new_member = await self.member_repo.add_member(member_data)
            created_members.append(new_member)

        await self.member_repo.db.commit()

        # Reload with user info
        results = []
        for m in created_members:
            full = await self.member_repo.get_by_id(
                m.member_id,
                eager_load_user=True
            )
            results.append(CareSpaceMemberRead.model_validate(full))

            notification_data = NotificationCreate(
                user_id=m.user_id,
                title="Added to Care Space",
                message=f"You have been added to the care space '{care_space.name}'.",
                link=f"/care_spaces/{care_space.care_space_id}"
            )
            await self.notification_service.create_notification(notification_data)

        return results
    
    # ---------------------------
    # UPDATE MEMBER
    # ---------------------------
    async def update_member(self, member_id: int, updates: CareSpaceMemberUpdate, current_user: User) -> CareSpaceMemberRead:
        """
        Update a member record (role or left_at).

        Only family owners can update member roles.
        """
        # Fetch member and validate permissions
        member = await self.member_repo.get_by_id(member_id, eager_load_user=True)
        checked_member = await self._get_member(member.care_space_id, current_user)
        ensure_family_owner(checked_member, current_user)

        # Update member record
        updated_member = await self.member_repo.update_member(member_id, updates)

        # Reload with eager loading for user AND care_space to avoid lazy-load
        updated_member = await self.member_repo.get_by_id(
            updated_member.member_id,
            eager_load_user=True,
            eager_load_care_space=True  # <--- make sure care_space is loaded
        )
        
        # Notify member about role change
        await self.notification_service.create_notification(
            NotificationCreate(
                user_id=updated_member.user_id,
                title="Care Space Role Updated",
                message=f"Your role in care space '{updated_member.care_space.name}' has been updated to '{updated_member.role_in_space}'.",
                link=f"/care_spaces/{updated_member.care_space_id}"
            )
        )
        return CareSpaceMemberRead.model_validate(updated_member)
    
    async def get_member_by_user_id(self, care_space_id: int, user_id: int):
        member = await self.member_repo.get_member(care_space_id, user_id)
        if not member:
            raise care_space_member_not_found_exception
        return member


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
        # Fetch member
        member = await self.member_repo.get_by_id(member_id, eager_load_user=True)
        if not member:
            raise HTTPException(status_code=404, detail="Care space member not found")

        # Check current user's membership and permissions
        checked_member = await self._get_member(member.care_space_id, current_user)
        ensure_family_owner(checked_member, current_user)

        # Remove member
        await self.member_repo.remove_member(member)

        # Explicitly fetch care space to avoid lazy-loading issues
        care_space = await self.care_space_repo.get_by_id(member.care_space_id)
        if not care_space:
            # Fallback in case care space no longer exists
            care_space_name = "Unknown Care Space"
            care_space_id = member.care_space_id
        else:
            care_space_name = care_space.name
            care_space_id = care_space.care_space_id

        notification_data = NotificationCreate(
            user_id=member.user_id,
            title="Removed from Care Space",
            message=f"You have been removed from care space '{care_space_name}'.",
            link=f"/care_spaces/{care_space_id}"
        )
        await self.notification_service.create_notification(notification_data)

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
    
    async def count_user_care_spaces(self, user_id: int) -> int:
        """
        Count the number of care spaces a user belongs to.
        """
        return await self.member_repo.count_by_user(user_id)
    