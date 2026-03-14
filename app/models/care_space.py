"""
models/care_space.py

This module defines the CareSpace ORM model for SQLAlchemy.

A CareSpace represents a collaborative caregiving space where multiple users 
(caregivers) can manage dependents together.

Fields:
- care_space_id: Primary key for the care space
- name: Name of the care space
- description: Optional description
- created_by: Foreign key linking to the user who created the space
- created_at: Timestamp when the care space was created
- updated_at: Timestamp of the last update
- expires_at: Optional timestamp when the care space code expires

Relationships:
- creator: Many-to-one relationship with the User who created the space
- members: One-to-many relationship with CareSpaceMember
- join_codes: One-to-many relationship with CareSpaceJoinCode
- 
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func  # For server_default timestamps

# ---------------------------
# Local App Imports
# ---------------------------
from app.core.database import Base


# ---------------------------
# CareSpace Model
# ---------------------------
class CareSpace(Base):
    """
    SQLAlchemy model representing a collaborative caregiving space.

    Allows multiple users to manage dependents and tasks together.
    """

    __tablename__ = "care_spaces"

    # ---------------------------
    # Columns
    # ---------------------------
    care_space_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Primary key for the care space"
    )

    name = Column(
        String(100),
        nullable=False,
        doc="Name of the care space"
    )

    description = Column(
        Text,
        nullable=True,
        doc="Optional description for the care space"
    )

    created_by = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        doc="User ID of the creator of the care space"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the care space was created"
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        doc="Timestamp of the last update"
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp when the care space code expires; null if permanent"
    )

    # ---------------------------
    # Relationships
    # ---------------------------
    creator = relationship(
        "User",
        back_populates="created_care_spaces",
        foreign_keys=[created_by],
        doc="Relationship to the user who created this care space"
    )

    members = relationship(
        "CareSpaceMember",
        back_populates="care_space",
        cascade="all, delete-orphan",
        doc="Members (caregivers) who belong to this care space"
    )

    join_codes = relationship(
        "CareSpaceJoinCode",
        back_populates="care_space",
        cascade="all, delete-orphan",
        doc="Join codes generated for this care space"
    )

    tasks = relationship(
        "Task",
        back_populates="care_space",
        cascade="all, delete-orphan",
        doc="One-to-many relationship to tasks"
    )