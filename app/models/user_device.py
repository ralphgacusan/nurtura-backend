# app/models/user_device.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserDevice(Base):
    __tablename__ = "user_devices"

    device_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    fcm_token = Column(String, nullable=False)

    user = relationship("User", back_populates="devices")