# routers/notification.py

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated, List

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import APIRouter, Depends, HTTPException

# ---------------------------
# Local App Imports
# ---------------------------
from app.schemas.notification import (
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
    NotificationStatus
)
from app.services.notification import NotificationService
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.notification import (
    get_notification_service,
    get_user_device_repo
)
from app.repositories.user_device import UserDeviceRepository

# ---------------------------
# Router Configuration
# ---------------------------
router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

# ---------------------------
# Create Notification Endpoint
# ---------------------------
@router.post("/", response_model=NotificationRead, description="Create a new notification for a user.")
async def create_notification(
    notification_data: NotificationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    notification_service: NotificationService = Depends(get_notification_service),
    user_device_repo: UserDeviceRepository = Depends(get_user_device_repo),
):
    """
    Create a notification for a user.
    """
    notification = await notification_service.create_notification(notification_data)

    # Fetch user devices for push notification
    user_devices = await user_device_repo.list_by_user(notification.user_id)
    fcm_tokens = [d.fcm_token for d in user_devices]

    # Send push notification
    await notification_service.send_push_notification(
        fcm_tokens, notification_data.title, notification_data.message
    )
    
    return notification

# ---------------------------
# List Notifications for Current User
# ---------------------------
@router.get("/me", response_model=List[NotificationRead], description="Get all notifications for the logged-in user.")
async def list_my_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    status: NotificationStatus | None = None,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Retrieve all notifications for the authenticated user.
    """
    return await notification_service.list_notifications_for_user(
        current_user, status=status
    )
# ---------------------------
# Get Single Notification
# ---------------------------
@router.get("/{notification_id}", response_model=NotificationRead)
async def get_notification(
    notification_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Retrieve a single notification by ID for the authenticated user.
    """
    notification = await notification_service.get_notification_by_id(notification_id)
    if notification.user_id != current_user.user_id: 
        raise HTTPException(status_code=403, detail="Not authorized to access this notification.")
    return notification

# ---------------------------
# Update Notification
# ---------------------------
@router.put("/{notification_id}", response_model=NotificationRead)
async def update_notification(
    notification_id: int,
    updates: NotificationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Update a notification by ID for the authenticated user.
    """
    notification = await notification_service.get_notification_by_id(notification_id)
    if notification.user_id != current_user.user_id:  
        raise HTTPException(status_code=403, detail="Not authorized to update this notification.")
    return await notification_service.update_notification(notification_id, updates)

# ---------------------------
# Mark Notification as Read
# ---------------------------
@router.patch("/{notification_id}/read", response_model=NotificationRead)
async def mark_as_read(
    notification_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Mark a notification as read for the authenticated user.
    """
    notification = await notification_service.get_notification_by_id(notification_id)
    if notification.user_id != current_user.user_id:  
        raise HTTPException(status_code=403, detail="Not authorized to mark this notification as read.")
    return await notification_service.mark_as_read(notification_id)

# ---------------------------
# Bulk Delete Notifications for Current User
# ---------------------------
@router.delete("/me", response_model=dict)
async def delete_all_my_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Delete all notifications for the authenticated user.
    """
    deleted_count = await notification_service.delete_all_notifications_for_user(current_user)
    return {"deleted_count": deleted_count}

# ---------------------------
# Delete Notification
# ---------------------------
@router.delete("/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Delete a single notification by ID for the authenticated user.
    """
    notification = await notification_service.get_notification_by_id(notification_id)
    if notification.user_id != current_user.user_id: 
        raise HTTPException(status_code=403, detail="Not authorized to delete this notification.")
    deleted = await notification_service.delete_notification(notification_id)
    return {"deleted": deleted}