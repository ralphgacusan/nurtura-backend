"""
dependencies/care_space.py

This module provides FastAPI dependency injection for CareSpace-related operations.
It defines:

- Repository dependencies for database access
- Service dependencies that use the repositories

These dependencies can be injected into route functions or other services
using FastAPI's `Depends`.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated  # For type hints with FastAPI Depends

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import Depends  # Dependency injection

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy.ext.asyncio import AsyncSession  # Async DB session

# ---------------------------
# Local Application Imports
# ---------------------------
from app.core.database import get_session
from app.dependencies.notification import get_notification_service
from app.repositories.user import UserRepository
from app.repositories.dependent_profile import DependentProfileRepository 
from app.repositories.care_space import CareSpaceRepository
from app.repositories.care_space_member import CareSpaceMemberRepository
from app.repositories.care_space_join_code import CareSpaceJoinCodeRepository

from app.services.care_space import CareSpaceService
from app.services.care_space_member import CareSpaceMemberService
from app.services.care_space_join_code import CareSpaceJoinCodeService
from app.services.notification import NotificationService

# ---------------------------
# Repository Dependencies
# ---------------------------
async def get_care_space_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> CareSpaceRepository:
    """
    Provide a CareSpaceRepository instance using the current database session.

    Args:
        session (AsyncSession): Async DB session provided by get_session

    Returns:
        CareSpaceRepository: Repository for care space operations
    """
    return CareSpaceRepository(session)


async def get_care_space_member_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> CareSpaceMemberRepository:
    """
    Provide a CareSpaceMemberRepository instance using the current database session.

    Args:
        session (AsyncSession): Async DB session provided by get_session

    Returns:
        CareSpaceMemberRepository: Repository for care space member operations
    """
    return CareSpaceMemberRepository(session)


async def get_care_space_join_code_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> CareSpaceJoinCodeRepository:
    """
    Provide a CareSpaceJoinCodeRepository instance using the current database session.

    Args:
        session (AsyncSession): Async DB session provided by get_session

    Returns:
        CareSpaceJoinCodeRepository: Repository for care space join code operations
    """
    return CareSpaceJoinCodeRepository(session)


async def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> UserRepository:
    """
    Provide a UserRepository instance using the current database session.

    Args:
        session (AsyncSession): Async DB session provided by get_session

    Returns:
        UserRepository: Repository for user operations
    """
    return UserRepository(session)


async def get_dependent_profile_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> DependentProfileRepository:
    """
    Provide a DependentProfileRepository instance using the current database session.

    Args:
        session (AsyncSession): Async DB session provided by get_session

    Returns:
        DependentProfileRepository: Repository for dependent profile operations
    """
    return DependentProfileRepository(session)


# ---------------------------
# Service Dependencies
# ---------------------------
async def get_care_space_member_service(
    member_repo: Annotated[CareSpaceMemberRepository, Depends(get_care_space_member_repo)],
    care_space_repo: Annotated[CareSpaceRepository, Depends(get_care_space_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    notification_service: Annotated[NotificationService, Depends(get_notification_service)],  # ← added

) -> CareSpaceMemberService:
    """
    Provide CareSpaceMemberService with all required repositories injected.

    Args:
        member_repo (CareSpaceMemberRepository): Repository for care space members
        care_space_repo (CareSpaceRepository): Repository for care spaces
        user_repo (UserRepository): Repository for users

    Returns:
        CareSpaceMemberService: Service instance for business logic
    """
    return CareSpaceMemberService(member_repo, care_space_repo, user_repo, notification_service=notification_service)


async def get_care_space_service(
    care_space_repo: Annotated[CareSpaceRepository, Depends(get_care_space_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    member_repo: Annotated[CareSpaceMemberRepository, Depends(get_care_space_member_repo)],
    notification_service: Annotated[NotificationService, Depends(get_notification_service)],  
) -> CareSpaceService:
    """
    Provide CareSpaceService instance with required repositories and services injected.

    Args:
        care_space_repo (CareSpaceRepository): Repository for care spaces
        user_repo (UserRepository): Repository for users
        member_repo (CareSpaceMemberRepository): Repository for care space members
        notification_service (NotificationService): Notification service for in-app notifications

    Returns:
        CareSpaceService: Service instance for care space business logic
    """
    return CareSpaceService(
        care_space_repo=care_space_repo,
        user_repo=user_repo,
        member_repo=member_repo,
        notification_service=notification_service  # ← inject here
    )


async def get_care_space_join_code_service(
    join_code_repo: Annotated[CareSpaceJoinCodeRepository, Depends(get_care_space_join_code_repo)],
    member_repo: Annotated[CareSpaceMemberRepository, Depends(get_care_space_member_repo)]
) -> CareSpaceJoinCodeService:
    """
    Provide CareSpaceJoinCodeService instance with required repositories injected.

    Args:
        join_code_repo (CareSpaceJoinCodeRepository): Repository for join codes
        member_repo (CareSpaceMemberRepository): Repository for care space members

    Returns:
        CareSpaceJoinCodeService: Service instance for join code business logic
    """
    return CareSpaceJoinCodeService(
        join_code_repo=join_code_repo,
        member_repo=member_repo
    )