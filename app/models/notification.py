# ---------------------------
# models/notification.py
# ---------------------------
"""
Defines the Notification SQLAlchemy model.
Notifications belong to a user and can be read/unread.
They contain title, message, and timestamps.

Fields:
- notification_id: Primary key.
- user_id: FK to users.
- title: Short notification title.
- message: Detailed notification message.
- read: Boolean indicating if the notification was read.
- created_at: Timestamp of creation.
- updated_at: Timestamp of last update.

Relationships:
- user: Many-to-one with User.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


# ---------------------------
# Notification Model
# ---------------------------
class Notification(Base):
    """
    SQLAlchemy model representing a notification sent to a user.

    Attributes:
        notification_id (int): Primary key.
        user_id (int): Linked user.
        title (str): Short title of the notification.
        message (str): Detailed notification message.
        read (bool): Whether the notification has been read.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        user (User): Related user who receives the notification.
    """

    __tablename__ = "notifications"

    # ---------------------------
    # Columns
    # ---------------------------
    notification_id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        doc="Primary key for notification"
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        doc="FK to users who will receive this notification"
    )

    title = Column(
        String(100),
        nullable=False,
        doc="Short title of notification"
    )

    message = Column(
        Text,
        nullable=False,
        doc="Detailed notification message"
    )

    read = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the notification has been read"
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        doc="Creation timestamp"
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        doc="Last update timestamp"
    )

    # ---------------------------
    # Relationships
    # ---------------------------
    user = relationship(
        "User",
        back_populates="notifications",
        doc="Many-to-one relationship to user"
    )