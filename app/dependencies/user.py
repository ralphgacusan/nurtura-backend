"""
dependencies/user.py

This module provides FastAPI dependencies for user management.
It includes repository and service dependencies for injection into routes.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated  # for type hinting with FastAPI Depends

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import Depends  # for dependency injection in route functions

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy.ext.asyncio import AsyncSession  # async DB session for repository

# ---------------------------
# Local Application Imports
# ---------------------------
from app.core.database import get_session  # dependency to get DB session
from app.repositories.user import UserRepository  # user CRUD repository
from app.services.user import UserService  # business logic service for users

# ---------------------------
# Repository Dependency
# ---------------------------
async def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> UserRepository:
    """
    Provide a UserRepository instance using the current database session.

    Args:
        session (AsyncSession): The active database session dependency.

    Returns:
        UserRepository: Repository instance for user CRUD operations.
    """
    # Return repository bound to the active DB session
    return UserRepository(session)

# ---------------------------
# Service Dependency
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
    # Return service with injected repository for business logic
    return UserService(user_repo)