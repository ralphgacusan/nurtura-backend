"""
dependencies/dependent_profile.py

This module provides FastAPI dependencies for DependentProfile management.
It includes repository and service dependencies to be injected into route functions.

Usage:
    from app.dependencies.dependent_profile import get_dependent_profile_service
    service: DependentProfileService = Depends(get_dependent_profile_service)
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
from app.core.database import get_session  # DB session dependency
from app.repositories.dependent_profile import DependentProfileRepository
from app.repositories.user import UserRepository
from app.services.dependent_profile import DependentProfileService
from app.services.user import UserService

# ---------------------------
# Repository Dependencies
# ---------------------------
async def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> UserRepository:
    """
    Provide a UserRepository instance using the current database session.

    Args:
        session (AsyncSession): Active async database session.

    Returns:
        UserRepository: Repository for user CRUD operations.
    """
    return UserRepository(session)


async def get_dependent_profile_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> DependentProfileRepository:
    """
    Provide a DependentProfileRepository instance using the current database session.

    Args:
        session (AsyncSession): Active async database session.

    Returns:
        DependentProfileRepository: Repository for dependent profile CRUD operations.
    """
    return DependentProfileRepository(session)


# ---------------------------
# Service Dependencies
# ---------------------------
async def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)]
) -> UserService:
    """
    Provide a UserService instance with the UserRepository injected.

    Args:
        user_repo (UserRepository): Injected user repository dependency.

    Returns:
        UserService: Service handling business logic for users.
    """
    return UserService(user_repo)


async def get_dependent_profile_service(
    dependent_profile_repo: Annotated[DependentProfileRepository, Depends(get_dependent_profile_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> DependentProfileService:
    """
    Provide a DependentProfileService instance with required repositories and services injected.

    Args:
        dependent_profile_repo (DependentProfileRepository): Injected repository for dependent profiles.
        user_repo (UserRepository): Injected user repository.
        user_service (UserService): Injected user service dependency.

    Returns:
        DependentProfileService: Service handling business logic for dependent profiles.
    """
    return DependentProfileService(
        dependent_profile_repo=dependent_profile_repo,
        user_repo=user_repo,
        user_service=user_service
    )