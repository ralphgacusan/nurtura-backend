"""
repositories/dependent_profile.py

Repository for managing DependentProfile ORM objects.
Provides CRUD and query operations specifically for dependent profiles.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.dependent_profile import DependentProfile
from app.schemas.dependent_profile import DependentProfileStore, DependentProfileUpdate


class DependentProfileRepository:
    """
    Repository for interacting with DependentProfile records in the database.
    
    Args:
        db (AsyncSession): SQLAlchemy asynchronous session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db  # store async session for DB operations

    # ---------------------------
    # CREATE
    # ---------------------------
    async def create_dependent_profile(self, dependent_profile: DependentProfileStore) -> DependentProfile:
        """
        Create a new dependent profile in the database.

        Args:
            dependent_profile (DependentProfileStore): Pydantic schema with profile data.

        Returns:
            DependentProfile: Newly created profile instance with primary key populated.
        """
        db_profile = DependentProfile(
            user_id=dependent_profile.user_id,         # link to dependent's user account
            care_notes=dependent_profile.care_notes,   # optional notes
            created_by=dependent_profile.created_by    # family member / caregiver
        )
        self.db.add(db_profile)  # stage for insertion
        await self.db.flush()    # flush to DB (assigns PK)
        return db_profile

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_id(
        self, dependent_id: int, eager_load_user: bool = False, creator_id: Optional[int] = None
    ) -> Optional[DependentProfile]:
        """
        Retrieve a dependent profile by its ID.

        Args:
            dependent_id (int): Primary key of the dependent profile.
            eager_load_user (bool): Whether to load linked User object.
            creator_id (int | None): Filter by creator ID if provided.

        Returns:
            DependentProfile | None: Profile if found, else None.
        """
        stmt = select(DependentProfile).where(DependentProfile.dependent_id == dependent_id)

        if creator_id is not None:
            stmt = stmt.where(DependentProfile.created_by == creator_id)  # filter by creator

        if eager_load_user:
            stmt = stmt.options(selectinload(DependentProfile.user))      # eager load linked User

        result = await self.db.execute(stmt)
        return result.scalars().first()  # return first match or None

    async def get_by_user_id(
        self, user_id: int, eager_load_user: bool = False, creator_id: Optional[int] = None
    ) -> Optional[DependentProfile]:
        """
        Retrieve a dependent profile by the linked user's ID.

        Args:
            user_id (int): Linked user's primary key.
            eager_load_user (bool): Whether to load linked User object.
            creator_id (int | None): Filter by creator ID if provided.

        Returns:
            DependentProfile | None: Profile if found, else None.
        """
        stmt = select(DependentProfile).where(DependentProfile.user_id == user_id)

        if creator_id is not None:
            stmt = stmt.where(DependentProfile.created_by == creator_id)

        if eager_load_user:
            stmt = stmt.options(selectinload(DependentProfile.user))

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_creator(self, creator_id: int, eager_load_user: bool = False) -> List[DependentProfile]:
        """
        List all dependent profiles created by a specific family member / caregiver.

        Args:
            creator_id (int): User ID of the creator.
            eager_load_user (bool): Whether to load linked User objects.

        Returns:
            List[DependentProfile]: List of profiles.
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
    ) -> Optional[DependentProfile]:
        """
        Update a dependent profile with fields from the update schema.

        Args:
            dependent_id (int): ID of the profile to update.
            updates (DependentProfileUpdate): Pydantic schema with updated fields.
            creator_id (int): User ID of the creator performing the update.

        Returns:
            DependentProfile | None: Updated profile, or None if not found.
        """
        profile = await self.get_by_id(dependent_id, eager_load_user=True, creator_id=creator_id)
        if not profile:
            return None  # profile does not exist or belongs to another creator

        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)  # apply only set fields

        self.db.add(profile)     # stage changes
        await self.db.commit()   # commit update
        await self.db.refresh(profile)  # refresh from DB
        return profile

    # ---------------------------
    # DELETE
    # ---------------------------
    async def delete_dependent_profile(self, dependent_id: int, creator_id: int) -> bool:
        """
        Delete a dependent profile.

        Args:
            dependent_id (int): Profile ID to delete.
            creator_id (int): User ID of the creator performing deletion.

        Returns:
            bool: True if deleted, False if not found.
        """
        profile = await self.get_by_id(dependent_id, eager_load_user=True, creator_id=creator_id)
        if not profile:
            return False  # profile not found or unauthorized

        await self.db.delete(profile)  # remove from DB
        await self.db.commit()         # commit deletion
        return True