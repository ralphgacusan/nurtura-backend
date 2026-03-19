"""
repositories/care_space_member.py

Repository for managing CareSpaceMember ORM objects.
Handles CRUD operations and queries for care space memberships.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.care_space_member import CareSpaceMember
from app.schemas.care_space_member import CareSpaceMemberCreate, CareSpaceMemberUpdate


class CareSpaceMemberRepository:
    """
    Repository for interacting with CareSpaceMember records in the database.

    Args:
        db (AsyncSession): SQLAlchemy asynchronous session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db  # store async session for DB operations

    # ---------------------------
    # CREATE
    # ---------------------------
    async def add_member(self, member_data: CareSpaceMemberCreate) -> CareSpaceMember:
        """
        Add a new member to a care space.
        """
        # Create CareSpaceMember ORM instance from Pydantic schema
        db_member = CareSpaceMember(
            care_space_id=member_data.care_space_id,
            user_id=member_data.user_id,
            role_in_space=member_data.role_in_space
        )
        self.db.add(db_member)      # stage for insert
        await self.db.flush()       # flush changes to get PK
        return db_member

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_id(
        self, 
        member_id: int, 
        eager_load_user: bool = False
    ) -> CareSpaceMember | None:
        """
        Retrieve a care space member by membership ID.
        """
        stmt = select(CareSpaceMember).where(CareSpaceMember.member_id == member_id)

        # Optionally load the related user object
        if eager_load_user:
            stmt = stmt.options(selectinload(CareSpaceMember.user))

        result = await self.db.execute(stmt)
        return result.scalars().first()  # return first match or None

    async def list_by_care_space(
        self, 
        care_space_id: int, 
        eager_load_user: bool = False
    ) -> list[CareSpaceMember]:
        """
        List all members of a specific care space.
        """
        stmt = select(CareSpaceMember).where(CareSpaceMember.care_space_id == care_space_id)

        # Eager load user info if requested
        if eager_load_user:
            stmt = stmt.options(selectinload(CareSpaceMember.user))

        result = await self.db.execute(stmt)
        return result.scalars().all()  # return list of members

    async def get_by_user_and_space(
        self, 
        user_id: int, 
        care_space_id: int, 
        eager_load_user: bool = False
    ) -> CareSpaceMember | None:
        """
        Retrieve a member record by user and care space.
        """
        stmt = select(CareSpaceMember).where(
            CareSpaceMember.user_id == user_id,
            CareSpaceMember.care_space_id == care_space_id
        )

        # Optionally eager load user info
        if eager_load_user:
            stmt = stmt.options(selectinload(CareSpaceMember.user))

        result = await self.db.execute(stmt)
        return result.scalars().first()  # return single membership or None

    # ---------------------------
    # UPDATE
    # ---------------------------
    async def update_member(
        self, 
        member_id: int, 
        updates: CareSpaceMemberUpdate
    ) -> CareSpaceMember | None:
        """
        Update a member record.
        """
        # Fetch member first
        member = await self.get_by_id(member_id)
        if not member:
            return None  # no such member

        # Apply only fields that are set in the Pydantic schema
        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(member, field, value)

        self.db.add(member)      # mark as dirty
        await self.db.commit()   # persist changes
        await self.db.refresh(member)  # refresh object with updated values
        return member

    # ---------------------------
    # DELETE
    # ---------------------------
    async def remove_member(self, member: CareSpaceMember) -> bool:
        """
        Delete a member record (hard delete).
        """
        await self.db.delete(member)  # stage deletion
        await self.db.commit()        # persist deletion
        return True

    # ---------------------------
    # Utility / Convenience Methods
    # ---------------------------
    async def is_member(self, care_space_id: int, user_id: int) -> bool:
        """
        Check if a user is a member of a care space.
        """
        member = await self.get_by_user_and_space(user_id, care_space_id)
        return member is not None  # True if exists

    async def get_member(self, care_space_id: int, user_id: int) -> CareSpaceMember | None:
        """
        Retrieve a member by care space and user.
        """
        return await self.get_by_user_and_space(user_id, care_space_id)

    async def list_members(
        self, 
        care_space_id: int, 
        eager_load_user: bool = False
    ) -> list[CareSpaceMember]:
        """
        List all members of a care space (alias of list_by_care_space).
        """
        return await self.list_by_care_space(care_space_id, eager_load_user=eager_load_user)

    async def get_member_role(self, care_space_id: int, user_id: int) -> str | None:
        """
        Retrieve the role of a member in a care space.
        """
        member = await self.get_by_user_and_space(user_id, care_space_id)
        return member.role_in_space if member else None
    
    async def count_by_user(self, user_id: int) -> int:
        query = select(func.count(CareSpaceMember.care_space_id)).where(CareSpaceMember.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0