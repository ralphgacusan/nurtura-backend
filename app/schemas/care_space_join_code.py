"""
schemas/care_space_join_code.py

Pydantic schemas for CareSpaceJoinCode.
Used for input validation and output serialization.
"""

from datetime import datetime
from pydantic import BaseModel


# ---------------------------
# CREATE SCHEMA
# ---------------------------
class CareSpaceJoinCodeCreate(BaseModel):
    """
    Schema for creating a new CareSpaceJoinCode.

    Attributes:
        care_space_id (int): ID of the care space to associate the code with.
        role (str | None): Role assigned to users who join via this code. Defaults to 'viewer'.
    """
    care_space_id: int
    role: str


# ---------------------------
# READ SCHEMA
# ---------------------------
class CareSpaceJoinCodeRead(BaseModel):
    """
    Schema for reading a CareSpaceJoinCode.

    Attributes:
        code (str): The generated join code.
        care_space_id (int): ID of the associated care space.
        role (str): Role assigned to users joining via this code.
        expires_at (datetime | None): Optional expiration date of the join code.
    """
    code: str
    care_space_id: int
    role: str
    expires_at: datetime | None = None

    model_config = {
        "from_attributes": True  # Enables ORM mode for SQLAlchemy model
    }


class CareSpaceJoinRequest(BaseModel):
    code: str