"""
schemas/care_space_member.py

Pydantic schemas for CareSpaceMember.
Used for input validation and output serialization.
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Annotated, Literal, Optional

# ---------------------------
# Local Imports
# ---------------------------
from app.schemas.user import UserRead  # Optional nested user info


# ---------------------------
# BASE SCHEMA
# ---------------------------
class CareSpaceMemberBase(BaseModel):
    """
    Shared fields for CareSpaceMember schemas.

    Attributes:
        role_in_space (Literal): Role of the member within the care space ('owner', 'editor', 'viewer').
        care_space_id (int): ID of the associated care space.
    """
    role_in_space: Annotated[Literal["owner", "editor", "viewer"], None]
    care_space_id: int

    @property
    def can_manage_care_space(self) -> bool:
        """
        Determine if the member can manage the care space.

        Returns:
            bool: True if role is 'owner', else False.
        """
        return self.role_in_space == "owner"

    @property
    def can_manage_tasks(self) -> bool:
        """
        Determine if the member can manage tasks within the care space.

        Returns:
            bool: True if role is 'owner' or 'editor', else False.
        """
        return self.role_in_space in ("owner", "editor")


# ---------------------------
# CREATE SCHEMA
# ---------------------------
class CareSpaceMemberCreate(CareSpaceMemberBase):
    """
    Schema for adding a member to a care space.

    Attributes:
        user_id (int): ID of the user being added.
    """
    user_id: int


# ---------------------------
# READ SCHEMA
# ---------------------------
class CareSpaceMemberRead(CareSpaceMemberBase):
    """
    Schema for reading care space membership info.

    Attributes:
        member_id (int): Membership record ID.
        user_id (int): ID of the user.
        joined_at (datetime): Timestamp when the user joined the care space.
        left_at (datetime | None): Timestamp when the user left (optional).
        user (UserRead | None): Optional nested user info.
    """
    member_id: int
    user_id: int
    joined_at: datetime
    left_at: Optional[datetime] = None

    user: Optional[UserRead] = None

    model_config = {
        "from_attributes": True  # Enables ORM mode for SQLAlchemy models
    }


# ---------------------------
# UPDATE SCHEMA
# ---------------------------
class CareSpaceMemberUpdate(BaseModel):
    """
    Schema for updating a care space member.

    Attributes:
        role_in_space (Literal | None): Optional updated role for the member.
    """
    role_in_space: Literal["owner", "editor", "viewer"] | None = None