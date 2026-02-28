"""
repositories/dependent_profile.py

This module defines the DependentProfileRepository for performing CRUD operations
on the DependentProfile model using an asynchronous SQLAlchemy session.

Responsibilities:
- Create new dependent profiles
- Retrieve profiles by dependent_id, user_id, or creator
- Update dependent profile information
- Delete dependent profiles
"""

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# ---------------------------
# Local App Imports
# ---------------------------
from app.models import DependentProfile
from app.schemas.dependent_profile import DependentProfileCreate, DependentProfileStore, DependentProfileUpdate

# ---------------------------
# DependentProfile Repository
# ---------------------------
class DependentProfileRepository:
    """
    Repository for managing DependentProfile database operations.

    Attributes:
        db (AsyncSession): Asynchronous SQLAlchemy session.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with a database session.

        Args:
            db (AsyncSession): Asynchronous database session.
        """
        self.db = db

    # ---------------------------
    # CREATE
    # ---------------------------
    async def create_dependent_profile(self, dependent_profile: DependentProfileStore) -> DependentProfile:
        """
        Create a new dependent profile in the database.

        Args:
            dependent_profile (DependentProfileStore): Pydantic schema with dependent profile data.

        Returns:
            DependentProfile: Newly created dependent profile instance.
        """
        db_profile = DependentProfile(
            user_id=dependent_profile.user_id,
            care_notes=dependent_profile.care_notes,
            created_by=dependent_profile.created_by
        )
        self.db.add(db_profile)
        await self.db.flush()
        return db_profile

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_id(
        self, dependent_id: int, eager_load_user: bool = False, creator_id: int | None = None
    ) -> DependentProfile | None:
        """
        Retrieve a dependent profile by its ID.

        Args:
            dependent_id (int): ID of the dependent profile.
            eager_load_user (bool, optional): Whether to load the linked user. Defaults to False.
            creator_id (int | None, optional): Restrict query to profiles created by this user. Defaults to None.

        Returns:
            DependentProfile | None: The dependent profile if found, else None.
        """
        stmt = select(DependentProfile).where(DependentProfile.dependent_id == dependent_id)
        if creator_id is not None:
            stmt = stmt.where(DependentProfile.created_by == creator_id)
        if eager_load_user:
            stmt = stmt.options(selectinload(DependentProfile.user))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_user_id(
        self, user_id: int, eager_load_user: bool = False, creator_id: int | None = None
    ) -> DependentProfile | None:
        """
        Retrieve a dependent profile by the linked user's ID.

        Args:
            user_id (int): ID of the linked user.
            eager_load_user (bool, optional): Whether to load the linked user. Defaults to False.
            creator_id (int | None, optional): Restrict query to profiles created by this user. Defaults to None.

        Returns:
            DependentProfile | None: The dependent profile if found, else None.
        """
        stmt = select(DependentProfile).where(DependentProfile.user_id == user_id)
        if creator_id is not None:
            stmt = stmt.where(DependentProfile.created_by == creator_id)
        if eager_load_user:
            stmt = stmt.options(selectinload(DependentProfile.user))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_creator(self, creator_id: int, eager_load_user: bool = False) -> list[DependentProfile]:
        """
        Fetch all dependent profiles created by a specific caregiver.

        Args:
            creator_id (int): ID of the caregiver who created the profiles.
            eager_load_user (bool, optional): Whether to load the linked user for each profile. Defaults to False.

        Returns:
            list[DependentProfile]: List of dependent profiles created by the caregiver.
        """
        stmt = select(DependentProfile).where(DependentProfile.created_by == creator_id)
        if eager_load_user:
            stmt = stmt.options(selectinload(DependentProfile.user))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ---------------------------
    # UPDATE
    # ---------------------------
    async def update_dependent_profile(
        self, dependent_id: int, updates: DependentProfileUpdate, creator_id: int
    ) -> DependentProfile | None:
        """
        Update fields of a dependent profile.

        Only the fields provided in `updates` will be modified.

        Args:
            dependent_id (int): ID of the dependent profile to update.
            updates (DependentProfileUpdate): Pydantic schema containing updated fields.
            creator_id (int): ID of the caregiver attempting the update.

        Returns:
            DependentProfile | None: The updated dependent profile, or None if not found.
        """
        profile = await self.get_by_id(dependent_id, eager_load_user=True, creator_id=creator_id)
        if not profile:
            return None

        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)

        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    # ---------------------------
    # DELETE
    # ---------------------------
    async def delete_dependent_profile(self, dependent_id: int, creator_id: int) -> bool:
        """
        Delete a dependent profile.

        Args:
            dependent_id (int): ID of the dependent profile to delete.
            creator_id (int): ID of the caregiver attempting the deletion.

        Returns:
            bool: True if deletion succeeded, False if profile not found.
        """
        profile = await self.get_by_id(dependent_id, eager_load_user=True, creator_id=creator_id)
        if not profile:
            return False
        await self.db.delete(profile)
        await self.db.commit()
        return True