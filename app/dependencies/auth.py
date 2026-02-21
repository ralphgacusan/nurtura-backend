"""
dependencies/auth.py

This module provides dependencies for authentication and authorization in FastAPI.
It includes:
- Repository dependencies
- Service dependencies
- OAuth2 token handling
- Current user retrieval and active user enforcement
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer  # for OAuth2 password flow

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy.ext.asyncio import AsyncSession  # async session for DB

# ---------------------------
# Local Application Imports
# ---------------------------
from app.core.database import get_session  # DB session dependency
from app.core.config import settings  # API prefix and secrets
from app.core.security import decode_token  # JWT decoding utility
from app.core.exceptions import inactive_user_exception, credentials_exception
from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.services.auth import AuthService
from app.schemas.user import UserStatus, UserRead

# ---------------------------
# API Prefix
# ---------------------------
api_prefix = settings.API_PREFIX  # dynamically used in OAuth2 token URL

# ---------------------------
# Repository Dependencies
# ---------------------------
async def get_user_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> UserRepository:
    """
    Return a UserRepository instance using the current database session.

    Args:
        session: AsyncSession dependency.

    Returns:
        UserRepository: repository for user CRUD operations.
    """
    return UserRepository(session)


async def get_refresh_repo(session: Annotated[AsyncSession, Depends(get_session)]) -> RefreshTokenRepository:
    """
    Return a RefreshTokenRepository instance using the current database session.

    Args:
        session: AsyncSession dependency.

    Returns:
        RefreshTokenRepository: repository for refresh token CRUD operations.
    """
    return RefreshTokenRepository(session)

# ---------------------------
# Service Dependencies
# ---------------------------
async def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    refresh_repo: Annotated[RefreshTokenRepository, Depends(get_refresh_repo)]
) -> AuthService:
    """
    Return an AuthService instance with user and refresh repositories injected.

    Args:
        user_repo: UserRepository instance.
        refresh_repo: RefreshTokenRepository instance.

    Returns:
        AuthService: authentication service with injected repos.
    """
    return AuthService(user_repo, refresh_repo)

# ---------------------------
# OAuth2 Configuration
# ---------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{api_prefix}/auth/token")
# This defines how FastAPI retrieves the token from Authorization header

# ---------------------------
# Current User Dependencies
# ---------------------------
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserRead:
    """
    Decode the access token and return the corresponding user.

    Args:
        token: JWT from Authorization header.
        user_repo: repository to fetch the user from DB.

    Raises:
        credentials_exception: if token is invalid or user does not exist.

    Returns:
        UserRead: current authenticated user.
    """
    user_id = int(decode_token(token))  # decode JWT to extract user_id
    user = await user_repo.get_by_id(user_id=user_id)  # fetch user from DB

    if not user:
        raise credentials_exception  # user not found

    return user


async def get_current_active_user(
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> UserRead:
    """
    Ensure that the current user is active.

    Args:
        current_user: UserRead object fetched from token.

    Raises:
        inactive_user_exception: if the user status is inactive.

    Returns:
        UserRead: active user.
    """
    if current_user.status == UserStatus.inactive:
        raise inactive_user_exception
    return current_user