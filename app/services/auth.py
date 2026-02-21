"""
services/auth.py

This module provides authentication services for users,
including login, token refresh, and logout operations.

Features:
- Authenticate user credentials
- Issue access and refresh tokens
- Rotate refresh tokens on refresh
- Logout single or all devices
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timedelta, timezone  # for token expiry handling

# ---------------------------
# Local App Imports
# ---------------------------
from app.repositories.user import UserRepository  # user CRUD operations
from app.repositories.refresh_token import RefreshTokenRepository  # refresh token CRUD
from app.schemas.user import UserLogin  # login request schema
from app.schemas.token import Token, RefreshTokenCreate  # token schemas
from app.core.security import (
    verify_password,  # check plaintext vs hashed passwords
    create_access_token,  # generate JWT access token
    create_refresh_token,  # generate JWT refresh token
    get_token_hash,  # hash refresh tokens for DB storage
    DUMMY_HASH,  # dummy hash for timing attack mitigation
    REFRESH_TOKEN_EXPIRE_DAYS,  # refresh token expiry duration
)
from app.models.user import User  # user model
from app.core.exceptions import invalid_credentials_exception, invalid_refresh_token_exception  # reusable exceptions

# ---------------------------
# Auth Service Class
# ---------------------------
class AuthService:
    """
    Service handling user authentication and token management.
    """

    def __init__(self, user_repo: UserRepository, refresh_repo: RefreshTokenRepository):
        self.user_repo = user_repo  # user repository
        self.refresh_repo = refresh_repo  # refresh token repository

    # -----------------------
    # Authenticate user
    # -----------------------
    async def authenticate_user(self, username: str, password: str) -> User:
        """
        Verify username and password. Raises invalid_credentials_exception on failure.
        Implements timing attack mitigation using DUMMY_HASH.
        """
        user = await self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            verify_password(password, DUMMY_HASH)  # mitigate timing attacks
            raise invalid_credentials_exception
        return user

    # -----------------------
    # Login (issue access + refresh tokens)
    # -----------------------
    async def login(self, login_data: UserLogin) -> Token:
        """
        Authenticate user and issue JWT access and refresh tokens.
        Stores hashed refresh token in database.
        """
        user = await self.authenticate_user(login_data.username, login_data.password)

        # Create access token
        access_token = create_access_token(user)

        # Create raw refresh token
        raw_refresh_token = create_refresh_token(user)
        hashed_refresh_token = get_token_hash(raw_refresh_token)  # hash before DB storage

        # Calculate token expiry
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # Prepare refresh token schema
        refresh_token_schema = RefreshTokenCreate(
            user_id=user.user_id,
            token_hash=hashed_refresh_token,
            expires_at=expires_at,
            device_info=getattr(login_data, "device_info", None),
            ip_address=getattr(login_data, "ip_address", None)
        )

        # Store refresh token in DB
        await self.refresh_repo.create(refresh_token_schema)

        # Return token response
        return Token(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
            username=user.username,
            role=user.role.value
        )

    # -----------------------
    # Refresh access + refresh tokens
    # -----------------------
    async def refresh(self, raw_refresh_token: str) -> Token:
        """
        Validate existing refresh token and issue new access + refresh tokens.
        Rotates refresh token in DB.
        """
        hashed_refresh_token = get_token_hash(raw_refresh_token)
        db_token = await self.refresh_repo.get_by_hash(hashed_refresh_token)

        # Check token validity
        if not db_token or db_token.revoked or db_token.expires_at < datetime.now(timezone.utc):
            raise invalid_refresh_token_exception

        # Get user
        user = await self.user_repo.get_by_id(db_token.user_id)
        if not user:
            raise invalid_refresh_token_exception

        # Issue new tokens
        access_token = create_access_token(user)
        new_raw_refresh_token = create_refresh_token(user)
        new_hashed_refresh_token = get_token_hash(new_raw_refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # Prepare new refresh token schema
        new_token_schema = RefreshTokenCreate(
            user_id=user.user_id,
            token_hash=new_hashed_refresh_token,
            expires_at=expires_at,
            device_info=db_token.device_info,
            ip_address=db_token.ip_address
        )

        # Rotate refresh token in DB
        await self.refresh_repo.rotate(old_token=db_token, new_token_data=new_token_schema)

        # Return new token pair
        return Token(
            access_token=access_token,
            refresh_token=new_raw_refresh_token,
            token_type="bearer",
            username=user.username,
            role=user.role.value
        )

    # -----------------------
    # Logout single device
    # -----------------------
    async def logout(self, raw_refresh_token: str) -> None:
        """
        Revoke a single refresh token (logout from one session/device).
        """
        hashed_token = get_token_hash(raw_refresh_token)
        db_token = await self.refresh_repo.get_by_hash(hashed_token)
        if not db_token:
            raise invalid_refresh_token_exception

        await self.refresh_repo.revoke(db_token)

    # -----------------------
    # Logout all devices
    # -----------------------
    async def logout_all(self, user_id: int) -> None:
        """
        Revoke all refresh tokens for the user (logout from all devices).
        """
        await self.refresh_repo.revoke_all_user_tokens(user_id)