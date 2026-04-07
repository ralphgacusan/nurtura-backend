# dependencies/notification.py

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import Depends

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------
# Local App Imports
# ---------------------------
from app.core.database import get_session
from app.repositories.notification import NotificationRepository
from app.repositories.user_device import UserDeviceRepository
from app.services.notification import NotificationService


# ---------------------------
# Repository Dependencies
# ---------------------------
async def get_notification_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> NotificationRepository:
    """
    Provide a NotificationRepository instance using the current DB session.
    """
    return NotificationRepository(session)


async def get_user_device_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> UserDeviceRepository:
    """
    Provide a UserDeviceRepository instance using the current DB session.
    """
    return UserDeviceRepository(session)


# ---------------------------
# Service Dependency
# ---------------------------
async def get_notification_service(
    notification_repo: Annotated[NotificationRepository, Depends(get_notification_repo)],
) -> NotificationService:
    """
    Provide a NotificationService instance with required repositories injected.
    """
    return NotificationService(notification_repo=notification_repo)