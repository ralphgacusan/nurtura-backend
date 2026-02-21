"""
repositories/refresh_token.py

Handles CRUD operations for RefreshToken objects in the database.

Includes:
- Creating refresh tokens
- Retrieving tokens by hash
- Revoking single or all tokens
- Rotating tokens during refresh flow
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone  # for timestamps

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy.ext.asyncio import AsyncSession  # async DB session
from sqlalchemy import select, update  # query constructs

# ---------------------------
# Local App Imports
# ---------------------------
from app.models.refresh_token import RefreshToken  # SQLAlchemy model
from app.schemas.token import RefreshTokenCreate  # Pydantic schema

# ---------------------------
# RefreshToken Repository
# ---------------------------
class RefreshTokenRepository:
    """
    Repository for managing RefreshToken database operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db  # async database session

    # ---------------------------
    # CREATE
    # ---------------------------
    async def create(self, token_data: RefreshTokenCreate) -> RefreshToken:
        """
        Create a new refresh token for a user.
        """
        refresh_token = RefreshToken(
            user_id=token_data.user_id,  # FK to user
            token_hash=token_data.token_hash,  # hashed token for storage
            expires_at=token_data.expires_at,  # expiration datetime
            device_info=token_data.device_info,  # optional device info
            ip_address=token_data.ip_address,  # optional IP address
        )
        self.db.add(refresh_token)  # stage new token
        await self.db.commit()  # persist to DB
        await self.db.refresh(refresh_token)  # refresh to get generated ID
        return refresh_token

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        """
        Retrieve a refresh token by its hashed value.
        Returns None if not found.
        """
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalars().first()

    # ---------------------------
    # UPDATE / REVOKE
    # ---------------------------
    async def revoke(self, token: RefreshToken) -> None:
        """
        Revoke a single refresh token (logout from one device).
        Sets revoked=True and records revoked_at timestamp.
        """
        token.revoked = True
        token.revoked_at = datetime.now(timezone.utc)
        await self.db.commit()  # persist changes

    async def rotate(
        self,
        old_token: RefreshToken,
        new_token_data: RefreshTokenCreate
    ) -> RefreshToken:
        """
        Rotate a refresh token during the refresh flow.

        Steps:
        1. Revoke the old token
        2. Create a new token
        3. Link old token's replaced_by_token_id to the new token
        """
        # Revoke old token
        old_token.revoked = True
        old_token.revoked_at = datetime.now(timezone.utc)

        # Create new token
        new_token = RefreshToken(
            user_id=new_token_data.user_id,
            token_hash=new_token_data.token_hash,
            expires_at=new_token_data.expires_at,
            device_info=new_token_data.device_info,
            ip_address=new_token_data.ip_address,
        )
        self.db.add(new_token)
        await self.db.flush()  # flush to assign new_token.token_id

        # Link old token to new token
        old_token.replaced_by_token_id = new_token.token_id

        await self.db.commit()  # commit both updates
        await self.db.refresh(new_token)  # refresh to ensure all fields populated

        return new_token

    async def revoke_all_user_tokens(self, user_id: int) -> None:
        """
        Revoke all active refresh tokens for a user (logout all devices).
        """
        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,  # filter by user
                RefreshToken.revoked == False      # only revoke active tokens
            )
            .values(
                revoked=True,
                revoked_at=datetime.now(timezone.utc)
            )
        )
        await self.db.commit()