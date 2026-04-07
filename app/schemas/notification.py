# ---------------------------
# schemas/notification.py
# ---------------------------
"""
Pydantic schemas for Notification operations.

Features:
- Base notification schema
- Notification creation schema
- Notification read schema
- Notification update schema
- Supports read/unread status
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime
from enum import Enum

# ---------------------------
# Pydantic Imports
# ---------------------------
from pydantic import BaseModel, Field
from typing import Annotated

# ---------------------------
# Local App Imports
# ---------------------------
from app.models.notification import Notification

# ---------------------------
# BASE NOTIFICATION SCHEMA
# ---------------------------
class NotificationBase(BaseModel):
    """
    Base schema shared by notification creation, read, and update schemas.

    Attributes:
        user_id (int): User who receives the notification
        title (str): Short title
        message (str): Detailed message
        read (bool): Whether it has been read
    """
    user_id: int

    title: Annotated[
        str,
        Field(min_length=1, max_length=100, strip_whitespace=True)
    ]

    message: Annotated[
        str,
        Field(min_length=1, max_length=1000)
    ]

    read: bool = False


# ---------------------------
# NOTIFICATION CREATE SCHEMA
# ---------------------------
class NotificationCreate(NotificationBase):
    """
    Schema for creating a notification.
    """
    pass


# ---------------------------
# NOTIFICATION READ SCHEMA
# ---------------------------
class NotificationRead(NotificationBase):
    """
    Schema for reading notification data.

    Attributes:
        notification_id (int)
        created_at (datetime)
        updated_at (datetime)
    """
    notification_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# ---------------------------
# NOTIFICATION UPDATE SCHEMA
# ---------------------------
class NotificationUpdate(BaseModel):
    """
    Schema for updating a notification (PATCH).
    All fields optional.
    """
    title: Annotated[
        str | None,
        Field(min_length=1, max_length=100, strip_whitespace=True)
    ] = None

    message: Annotated[
        str | None,
        Field(min_length=1, max_length=1000)
    ] = None

    read: bool | None = None


# ---------------------------
# NOTIFICATION STATUS ENUM
# ---------------------------
class NotificationStatus(str, Enum):
    unread = "unread"
    read = "read"