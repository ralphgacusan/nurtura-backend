"""
schemas/care_space.py

Pydantic schemas for CareSpace.
Used for input validation and output serialization.
Handles creation, reading, and updating of care spaces.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Annotated, Optional

# ---------------------------
# Local Imports
# ---------------------------
from app.schemas.user import UserRead  # Optional nested creator info
from app.schemas.care_space_member import CareSpaceMemberRead  # Optional nested members


# ---------------------------
# BASE SCHEMA
# ---------------------------
class CareSpaceBase(BaseModel):
    """
    Shared fields for CareSpace schemas.

    Attributes:
        name (str): Name of the care space (max 100 characters).
        description (str | None): Optional description (max 500 characters).
    """
    name: Annotated[str, Field(max_length=100)]
    description: Annotated[Optional[str], Field(max_length=500)] = None


# ---------------------------
# CREATE SCHEMA
# ---------------------------
class CareSpaceCreate(CareSpaceBase):
    """
    Schema for creating a new care space.

    Inherits all fields from CareSpaceBase.
    """
    pass


# ---------------------------
# READ SCHEMA
# ---------------------------
class CareSpaceRead(CareSpaceBase):
    """
    Schema for reading care space info.

    Attributes:
        care_space_id (int): Unique ID of the care space.
        created_by (int): ID of the user who created the care space.
        created_at (datetime): Timestamp when care space was created.
        updated_at (datetime | None): Timestamp of last update, if any.
        expires_at (datetime | None): Optional expiration timestamp.
        creator (UserRead | None): Nested creator user info.
        members (list[CareSpaceMemberRead] | None): Nested list of care space members.
    """
    care_space_id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    creator: Optional[UserRead] = None
    members: Optional[list[CareSpaceMemberRead]] = None

    model_config = {
        "from_attributes": True  # Enables ORM mode for SQLAlchemy models
    }


# ---------------------------
# UPDATE SCHEMA
# ---------------------------
class CareSpaceUpdate(BaseModel):
    """
    Schema for updating a care space (PATCH-style).

    Only the provided fields will be updated.
    
    Attributes:
        name (str | None): Optional new name of the care space.
        description (str | None): Optional new description.
    """
    name: Optional[str] = None
    description: Optional[str] = None