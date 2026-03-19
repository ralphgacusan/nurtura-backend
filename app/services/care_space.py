"""
services/care_space_service.py

Service layer for managing CareSpace operations.

Responsibilities:
- Create, read, update, delete care spaces
- Ensure proper permissions (family members, owners)
- List care spaces for a member
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timedelta, timezone
import random
import string

# ---------------------------
# Local App Imports
# ---------------------------
from app.repositories.care_space import CareSpaceRepository
from app.repositories.user import UserRepository
from app.repositories.care_space_member import CareSpaceMemberRepository
from app.schemas.care_space import CareSpaceCreate, CareSpaceUpdate, CareSpaceRead
from app.schemas.care_space_member import CareSpaceMemberCreate
from app.models.user import User
from app.core.permissions import ensure_family_member, ensure_member, ensure_family_owner
from app.core.exceptions import care_space_not_found_exception, user_not_found_exception
from app.core.config import settings

# ---------------------------
# CareSpace Service
# ---------------------------
class CareSpaceService:
    """
    Service for managing CareSpace operations.

    Permissions:
        - Only family members can create care spaces.
        - Only owners can update or delete care spaces.
    """

    def __init__(
        self,
        care_space_repo: CareSpaceRepository,
        user_repo: UserRepository,
        member_repo: CareSpaceMemberRepository,
    ):
        self.care_space_repo = care_space_repo
        self.user_repo = user_repo
        self.member_repo = member_repo

    # ---------------------------
    # PRIVATE: Get Member
    # ---------------------------
    async def _get_member(self, care_space_id: int, user: User):
        """
        Retrieve membership of a user in a care space.

        Args:
            care_space_id (int): Care space ID
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
    # CREATE CARESPACE
    # ---------------------------
    async def create_care_space(
        self,
        data: CareSpaceCreate,
        current_user: User
    ) -> CareSpaceRead:

        ensure_family_member(current_user)

        # 1. Create care space
        care_space = await self.care_space_repo.create_care_space(
            care_space=data,
            user_id=current_user.user_id
        )
        await self.care_space_repo.db.commit()

        # 2. Add creator as owner
        owner_member = CareSpaceMemberCreate(
            care_space_id=care_space.care_space_id,
            user_id=current_user.user_id,
            role_in_space="owner"
        )
        await self.member_repo.add_member(owner_member)

        # 3. OPTIONAL: Add dependents (bulk)
        if data.dependent_user_ids:
            for user_id in data.dependent_user_ids:

                # Optional: validate user exists
                user = await self.user_repo.get_by_id(user_id)
                if not user:
                    raise user_not_found_exception

                dependent_member = CareSpaceMemberCreate(
                    care_space_id=care_space.care_space_id,
                    user_id=user_id,
                    role_in_space="viewer"
                )
                await self.member_repo.add_member(dependent_member)

        await self.member_repo.db.commit()

        # 4. Reload with members
        care_space = await self.care_space_repo.get_by_id(
            care_space.care_space_id,
            eager_load=True
        )

        return CareSpaceRead.model_validate(care_space)

    # ---------------------------
    # GET CARESPACE BY ID
    # ---------------------------
    async def get_care_space(self, care_space_id: int, current_user: User) -> CareSpaceRead:
        """
        Retrieve care space info by ID.

        Args:
            care_space_id (int): Care space ID
            current_user (User): Current authenticated user

        Returns:
            CareSpaceRead: Care space details with members
        """
        await self._get_member(care_space_id, current_user)

        care_space = await self.care_space_repo.get_by_id(care_space_id, eager_load=True)
        if not care_space:
            raise care_space_not_found_exception

        return CareSpaceRead.model_validate(care_space)

    # ---------------------------
    # LIST CARESPACES FOR MEMBER
    # ---------------------------
    async def list_care_spaces_for_member(self, current_user: User) -> list[CareSpaceRead]:
        """
        List all care spaces where the current user is a member.

        Args:
            current_user (User): Authenticated user

        Returns:
            list[CareSpaceRead]: List of care spaces with members
        """
        care_spaces = await self.care_space_repo.list_by_member(user_id=current_user.user_id, eager_load=True)
        return [CareSpaceRead.model_validate(care_space) for care_space in care_spaces]

    # ---------------------------
    # UPDATE CARESPACE
    # ---------------------------
    async def update_care_space(self, care_space_id: int, updates: CareSpaceUpdate, current_user: User) -> CareSpaceRead:
        """
        Update a care space (PATCH-style).

        Only owners can update care spaces.

        Args:
            care_space_id (int): Care space ID
            updates (CareSpaceUpdate): Fields to update
            current_user (User): Authenticated user

        Returns:
            CareSpaceRead: Updated care space
        """
        member = await self._get_member(care_space_id, current_user)
        ensure_family_owner(member, current_user)

        care_space = await self.care_space_repo.get_by_id(care_space_id)
        if not care_space:
            raise care_space_not_found_exception

        await self.care_space_repo.update_care_space(care_space_id, updates)
        updated = await self.care_space_repo.get_by_id(care_space_id, eager_load=True)
        return CareSpaceRead.model_validate(updated)

    # ---------------------------
    # DELETE CARESPACE
    # ---------------------------
    async def delete_care_space(self, care_space_id: int, current_user: User) -> dict:
        """
        Delete a care space.

        Only owners can delete care spaces.

        Args:
            care_space_id (int): Care space ID
            current_user (User): Authenticated user

        Returns:
            dict: Success message
        """
        member = await self._get_member(care_space_id, current_user)
        ensure_family_owner(member, current_user)

        care_space = await self.care_space_repo.get_by_id(care_space_id)
        if not care_space:
            raise care_space_not_found_exception

        await self.care_space_repo.delete_care_space(care_space_id)
        await self.care_space_repo.db.commit()
        return {"detail": "Care space deleted successfully."}