"""
models/care_space_join_code.py

This module defines the CareSpaceJoinCode SQLAlchemy model, which represents
join codes used to invite members to a care space.

Attributes:
    code (str): Unique join code (primary key)
    care_space_id (int): Foreign key referencing the target care space
    role (str): Role assigned to the user joining via this code ("owner", "editor", "viewer")
    expires_at (datetime | None): Optional expiration datetime of the code
    is_used (bool): Flag indicating whether the code has been used
    care_space (relationship): SQLAlchemy relationship to the parent CareSpace
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

# ---------------------------
# PostgreSQL Enum for roles
# ---------------------------
# Reuse the existing enum type from DB (do not recreate it)
# Defines possible roles assigned via a join code
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
role_enum = PGEnum(
    "owner", "editor", "viewer",
    name="role_in_space_enum",
    create_type=False  # don't recreate in DB if already exists
)


class CareSpaceJoinCode(Base):
    """
    SQLAlchemy model for storing care space join codes.

    A join code allows a user to join a care space with a predefined role.
    """

    __tablename__ = "care_space_join_codes"

    # ---------------------------
    # Columns
    # ---------------------------
    code = Column(
        String(64),
        primary_key=True,
        index=True,
        doc="Unique join code for joining a care space"
    )

    care_space_id = Column(
        Integer,
        ForeignKey("care_spaces.care_space_id"),
        nullable=False,
        doc="ID of the care space this code belongs to"
    )

    role = Column(
        role_enum,
        nullable=False,
        default="viewer",
        doc="Role assigned to user joining via this code"
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Optional expiration datetime of the join code"
    )

    is_used = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Flag indicating whether this code has already been used"
    )

    # ---------------------------
    # Relationships
    # ---------------------------
    care_space = relationship(
        "CareSpace",
        back_populates="join_codes",
        doc="Relationship to parent CareSpace model"
    )