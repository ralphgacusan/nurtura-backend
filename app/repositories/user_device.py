# app/repositories/user_device.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user_device import UserDevice

class UserDeviceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_user(self, user_id: int) -> list[UserDevice]:
        result = await self.db.execute(select(UserDevice).where(UserDevice.user_id == user_id))
        return result.scalars().all()