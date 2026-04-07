# routers/user_device.py
from fastapi import APIRouter, Depends
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.models.user_device import UserDevice
from app.repositories.user_device import UserDeviceRepository
from pydantic import BaseModel
from app.dependencies.notification import get_notification_service

router = APIRouter(prefix="/user-device", tags=["user-device"])

class UserDeviceCreate(BaseModel):
    fcm_token: str

@router.post("/register")
async def register_device(
    data: UserDeviceCreate,
    current_user: User = Depends(get_current_user),
    repo: UserDeviceRepository = Depends(get_notification_service)
):
    # Check if token exists for this user
    devices = await repo.list_by_user(current_user.user_id)
    if any(d.fcm_token == data.fcm_token for d in devices):
        return {"message": "Device already registered"}
    
    # Add new device
    new_device = UserDevice(user_id=current_user.user_id, fcm_token=data.fcm_token)
    repo.db.add(new_device)
    await repo.db.commit()
    await repo.db.refresh(new_device)
    return {"message": "Device registered", "device_id": new_device.device_id}