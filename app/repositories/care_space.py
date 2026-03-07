"""
repositories/care_space.py

Repository for managing CareSpace ORM objects.
Provides CRUD and query operations specifically for care spaces.
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.care_space import CareSpace
from app.models.care_space_member import CareSpaceMember
from app.schemas.care_space import CareSpaceCreate, CareSpaceUpdate


class CareSpaceRepository:
    """
    Repository for interacting with CareSpace records in the database.
    
    Args:
        db (AsyncSession): SQLAlchemy asynchronous session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db  # store async session for DB operations

    # ---------------------------
    # CREATE
    # ---------------------------
    async def create_care_space(self, care_space: CareSpaceCreate, user_id: int) -> CareSpace:
        """
        Create a new care space with the given creator (user_id).
        """
        db_space = CareSpace(
            name=care_space.name,               # name of the care space
            description=care_space.description, # optional description
            created_by=user_id                  # assign creator
        )
        self.db.add(db_space)      # stage for insertion
        await self.db.flush()      # flush to DB (assigns PK)
        return db_space            # return unsaved ORM instance with PK populated

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_id(self, care_space_id: int, eager_load: bool = False) -> Optional[CareSpace]:
        """
        Retrieve a care space by its ID.

        Args:
            care_space_id (int): CareSpace primary key.
            eager_load (bool): Whether to eagerly load related creator and members.

        Returns:
            CareSpace | None: Care space object if found, else None.
        """
        stmt = select(CareSpace).where(CareSpace.care_space_id == care_space_id)

        if eager_load:
            stmt = stmt.options(
                selectinload(CareSpace.creator),                       # eager load creator
                selectinload(CareSpace.members).selectinload(CareSpaceMember.user)  # eager load members' user info
            )

        result = await self.db.execute(stmt)
        return result.scalars().first()  # return first match or None

    # ---------------------------
    # LIST / QUERY
    # ---------------------------
    async def list_by_member(self, user_id: int, eager_load: bool = False) -> List[CareSpace]:
        """
        List all care spaces where a given user is a member.
        """
        stmt = select(CareSpace).where(
            CareSpace.members.any(user_id=user_id)  # check membership relationship
        )

        if eager_load:
            stmt = stmt.options(
                selectinload(CareSpace.creator),                        # eager load creator
                selectinload(CareSpace.members).selectinload(CareSpaceMember.user)  # eager load member users
            )

        result = await self.db.execute(stmt)
        return result.scalars().all()  # return list of care spaces

    # ---------------------------
    # UPDATE
    # ---------------------------
    async def update_care_space(self, care_space_id: int, updates: CareSpaceUpdate) -> Optional[CareSpace]:
        """
        Update fields of a care space using a Pydantic update schema.
        """
        care_space = await self.get_by_id(care_space_id, eager_load=True)
        if not care_space:
            return None  # care space not found

        # apply only fields that were set in the update schema
        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(care_space, field, value)

        self.db.add(care_space)      # stage changes
        await self.db.commit()       # commit updates
        await self.db.refresh(care_space)  # refresh instance with DB state
        return care_space

    # ---------------------------
    # DELETE
    # ---------------------------
    async def delete_care_space(self, care_space_id: int) -> bool:
        """
        Delete a care space (hard delete) by ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        care_space = await self.get_by_id(care_space_id, eager_load=True)
        if not care_space:
            return False

        await self.db.delete(care_space)  # remove from DB
        await self.db.commit()             # commit deletion
        return True