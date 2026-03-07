"""
repositories/care_space_join_code.py

Repository for managing CareSpaceJoinCode ORM objects.
Provides CRUD and query operations specifically for join codes.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.care_space_join_code import CareSpaceJoinCode


class CareSpaceJoinCodeRepository:
    """
    Repository for interacting with CareSpaceJoinCode records in the database.
    
    Args:
        db (AsyncSession): SQLAlchemy asynchronous session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db  # store async session for DB operations

    # ---------------------------
    # CREATE
    # ---------------------------
    async def add(self, join_code: CareSpaceJoinCode) -> CareSpaceJoinCode:
        """
        Add a new CareSpaceJoinCode to the database.
        """
        self.db.add(join_code)        # stage ORM object for insert
        await self.db.commit()        # commit transaction
        await self.db.refresh(join_code)  # refresh object to get updated fields (e.g., defaults)
        return join_code

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_code(self, code: str) -> Optional[CareSpaceJoinCode]:
        """
        Retrieve a join code record by its code.
        """
        result = await self.db.execute(
            select(CareSpaceJoinCode).where(CareSpaceJoinCode.code == code)
        )
        return result.scalars().first()  # return single matching code or None

    # ---------------------------
    # QUERY / FILTER
    # ---------------------------
    async def get_active_codes(self, care_space_id: int) -> List[CareSpaceJoinCode]:
        """
        Get all active join codes for a given care space.

        A code is considered active if:
        - It has not been used (`is_used == False`), and
        - It has no expiration or expires in the future.
        """
        now = datetime.now(timezone.utc)  # current UTC timestamp
        result = await self.db.execute(
            select(CareSpaceJoinCode).where(
                and_(
                    CareSpaceJoinCode.care_space_id == care_space_id,  # match care space
                    CareSpaceJoinCode.is_used == False,                # must not be used
                    or_(
                        CareSpaceJoinCode.expires_at == None,         # no expiry
                        CareSpaceJoinCode.expires_at > now           # or expiry in future
                    )
                )
            )
        )
        return result.scalars().all()  # return list of active codes