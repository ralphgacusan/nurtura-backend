# services/notification_service.py

"""
Service layer for managing Notification operations.

Responsibilities:
- Create, read, update, delete notifications
- Mark notifications as read/unread
"""

# ---------------------------
# Local App Imports
# ---------------------------
from app.repositories.notification import NotificationRepository
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationRead,
    NotificationStatus
)
from app.models.user import User
from datetime import datetime, timezone
from fastapi import HTTPException
import httpx
import os

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")  # Firebase Console


# ---------------------------
# Notification Service
# ---------------------------
class NotificationService:
    """
    Service for handling notifications.
    """

    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    # ---------------------------
    # CREATE NOTIFICATION
    # ---------------------------
    async def create_notification(
        self,
        notification_data: NotificationCreate
    ) -> NotificationRead:
        notification = await self.notification_repo.create_notification(notification_data)
        return NotificationRead.model_validate(notification)

    # ---------------------------
    # GET NOTIFICATION BY ID
    # ---------------------------
    async def get_notification_by_id(
        self,
        notification_id: int
    ) -> NotificationRead:
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return NotificationRead.model_validate(notification)

    # ---------------------------
    # LIST NOTIFICATIONS FOR USER
    # ---------------------------
    async def list_notifications_for_user(
        self,
        user: User,
        status: NotificationStatus | None = None
    ) -> list[NotificationRead]:
        only_unread = status == NotificationStatus.unread if status else False
        notifications = await self.notification_repo.list_by_user(user.user_id, only_unread=only_unread)
        return [NotificationRead.model_validate(n) for n in notifications]

    # ---------------------------
    # UPDATE NOTIFICATION
    # ---------------------------
    async def update_notification(
        self,
        notification_id: int,
        updates: NotificationUpdate
    ) -> NotificationRead:
        notification = await self.notification_repo.update_notification(notification_id, updates)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return NotificationRead.model_validate(notification)

    # ---------------------------
    # MARK AS READ
    # ---------------------------
    async def mark_as_read(
        self,
        notification_id: int
    ) -> NotificationRead:
        notification = await self.notification_repo.mark_as_read(notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return NotificationRead.model_validate(notification)

    # ---------------------------
    # DELETE NOTIFICATION
    # ---------------------------
    async def delete_notification(
        self,
        notification_id: int
    ) -> bool:
        deleted = await self.notification_repo.delete_notification(notification_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Notification not found")
        return deleted

    # ---------------------------
    # BULK DELETE NOTIFICATIONS FOR USER
    # ---------------------------
    async def delete_all_notifications_for_user(
        self,
        user: User
    ) -> int:
        deleted_count = await self.notification_repo.delete_all_for_user(user.user_id)
        return deleted_count
    

    # ---------------------------
    # PUSH NOTIFICATIONS FOR USER
    # ---------------------------
    async def send_push_notification(self, fcm_tokens: list[str], title: str, message: str):
        if not fcm_tokens:
            return

        payload = {
            "registration_ids": fcm_tokens,
            "notification": {
                "title": title,
                "body": message,
            },
            "android": {"priority": "high"},
            "apns": {"headers": {"apns-priority": "10"}}
        }

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"key={FCM_SERVER_KEY}", "Content-Type": "application/json"}
            response = await client.post("https://fcm.googleapis.com/fcm/send", json=payload, headers=headers)
            return response.json()