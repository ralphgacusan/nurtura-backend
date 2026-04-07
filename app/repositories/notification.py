# repositories/notification.py

"""
Repository for managing Notification ORM objects.
Provides CRUD and query operations specifically for notifications.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate


class NotificationRepository:
    """
    Repository for interacting with Notification records in the database.
    
    Args:
        db (AsyncSession): SQLAlchemy asynchronous session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------------------------
    # CREATE
    # ---------------------------
    async def create_notification(self, notification: NotificationCreate) -> Notification:
        """
        Create a new notification in the database.
        """
        db_notification = Notification(
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            read=notification.read
        )
        self.db.add(db_notification)
        await self.db.commit()       # <-- commit transaction
        await self.db.refresh(db_notification)  # <-- refresh to get IDs
        return db_notification

    # ---------------------------
    # READ BY ID
    # ---------------------------
    async def get_by_id(self, notification_id: int) -> Notification | None:
        """
        Retrieve a notification by its ID.

        Args:
            notification_id (int): Notification primary key.

        Returns:
            Notification | None: Notification object if found, else None.
        """
        stmt = select(Notification).where(Notification.notification_id == notification_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    # ---------------------------
    # LIST / QUERY
    # ---------------------------
    async def list_by_user(self, user_id: int, only_unread: bool = False) -> list[Notification]:
        """
        List all notifications for a specific user.

        Args:
            user_id (int): User ID.
            only_unread (bool): If True, filter only unread notifications.
        """
        stmt = select(Notification).where(Notification.user_id == user_id)
        if only_unread:
            stmt = stmt.where(Notification.read == False)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ---------------------------
    # UPDATE
    # ---------------------------
    async def update_notification(self, notification_id: int, updates: NotificationUpdate) -> Notification | None:
        """
        Update fields of a notification using a Pydantic update schema.
        """
        notification = await self.get_by_id(notification_id)
        if not notification:
            return None

        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(notification, field, value)

        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    # ---------------------------
    # MARK AS READ
    # ---------------------------
    async def mark_as_read(self, notification_id: int) -> Notification | None:
        """
        Mark a notification as read.
        """
        notification = await self.get_by_id(notification_id)
        if not notification:
            return None

        notification.read = True
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    # ---------------------------
    # DELETE
    # ---------------------------
    async def delete_notification(self, notification_id: int) -> bool:
        """
        Delete a notification (hard delete) by ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        notification = await self.get_by_id(notification_id)
        if not notification:
            return False

        await self.db.delete(notification)
        await self.db.commit()
        return True

    # ---------------------------
    # BULK DELETE FOR USER
    # ---------------------------
    async def delete_all_for_user(self, user_id: int) -> int:
        """
        Delete all notifications for a specific user.

        Returns:
            int: Number of deleted notifications.
        """
        stmt = delete(Notification).where(Notification.user_id == user_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount