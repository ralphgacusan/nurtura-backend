"""
dependencies/care_space_member.py

This module provides FastAPI dependency injection functions for care space members.
It defines:
- Repository dependencies for database access
- Service dependencies that use the repositories

These dependencies are injected into routes or other services using FastAPI's `Depends`.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated  # for type hints with FastAPI dependencies

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import Depends  # dependency injection

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy.ext.asyncio import AsyncSession  # async session for DB operations

# ---------------------------
# Local Application Imports
# ---------------------------
from app.core.database import get_session  # provides AsyncSession for DB operations
from app.repositories.care_space_member import CareSpaceMemberRepository
from app.repositories.care_space import CareSpaceRepository
from app.repositories.user import UserRepository
from app.services.care_space_member import CareSpaceMemberService

# ---------------------------
# Repository Dependencies
# ---------------------------
async def get_care_space_member_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> CareSpaceMemberRepository:
    """
    Provides a CareSpaceMemberRepository instance for dependency injection.

    Args:
        session (AsyncSession): Async database session injected via get_session.

    Returns:
        CareSpaceMemberRepository: Repository for care space member operations.
    """
    return CareSpaceMemberRepository(session)


async def get_care_space_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> CareSpaceRepository:
    """
    Provides a CareSpaceRepository instance for dependency injection.

    Args:
        session (AsyncSession): Async database session injected via get_session.

    Returns:
        CareSpaceRepository: Repository for care space operations.
    """
    return CareSpaceRepository(session)


async def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> UserRepository:
    """
    Provides a UserRepository instance for dependency injection.

    Args:
        session (AsyncSession): Async database session injected via get_session.

    Returns:
        UserRepository: Repository for user operations.
    """
    return UserRepository(session)


# ---------------------------
# Service Dependency
# ---------------------------
async def get_care_space_member_service(
    member_repo: Annotated[CareSpaceMemberRepository, Depends(get_care_space_member_repo)],
    care_space_repo: Annotated[CareSpaceRepository, Depends(get_care_space_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> CareSpaceMemberService:
    """
    Provides a CareSpaceMemberService instance for dependency injection.

    Combines the member, care space, and user repositories into a single service
    for route or service layer usage.

    Args:
        member_repo (CareSpaceMemberRepository): Repository for care space members.
        care_space_repo (CareSpaceRepository): Repository for care spaces.
        user_repo (UserRepository): Repository for users.

    Returns:
        CareSpaceMemberService: Service that handles business logic for care space members.
    """
    return CareSpaceMemberService(member_repo, care_space_repo, user_repo)