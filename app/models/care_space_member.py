"""
models/care_space_member.py

This module defines the CareSpaceMember ORM model for SQLAlchemy.

A CareSpaceMember represents a user's membership in a care space and 
their permissions within that space.

Fields:
- member_id: Primary key for the membership record
- care_space_id: Foreign key referencing care_spaces.care_space_id
- user_id: Foreign key referencing users.user_id
- role_in_space: Role assigned to the user within the care space (owner, editor, viewer)
- joined_at: Timestamp when the user joined the care space
- left_at: Optional timestamp when the user left the care space (soft removal)

Relationships:
- care_space: Many-to-one relationship with CareSpace
- user: Many-to-one relationship with User
"""

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func  # For server_default timestamps

# ---------------------------
# Local App Imports
# ---------------------------
from app.core.database import Base


# ---------------------------
# CareSpaceMember Model
# ---------------------------
class CareSpaceMember(Base):
    """
    SQLAlchemy model representing a user's membership in a care space.

    Permissions and roles are assigned per care space.
    """

    __tablename__ = "care_space_members"

    # ---------------------------
    # Columns
    # ---------------------------
    member_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Primary key for the membership record"
    )

    care_space_id = Column(
        Integer,
        ForeignKey("care_spaces.care_space_id"),
        nullable=False,
        doc="Foreign key to the care space this membership belongs to"
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        doc="Foreign key to the user associated with this membership"
    )

    role_in_space = Column(
        Enum("owner", "editor", "viewer", name="role_in_space_enum"),
        nullable=False,
        doc="Role assigned to the user within the care space"
    )

    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the user joined the care space"
    )

    left_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Optional timestamp when the user left the care space (soft removal)"
    )

    # ---------------------------
    # Relationships
    # ---------------------------
    care_space = relationship(
        "CareSpace",
        back_populates="members",
        doc="Relationship to the parent CareSpace"
    )

    user = relationship(
        "User",
        back_populates="care_space_memberships",
        doc="Relationship to the associated User"
    )