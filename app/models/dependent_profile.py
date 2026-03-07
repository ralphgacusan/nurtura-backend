"""
models/dependent_profile.py

This module defines the DependentProfile ORM model for SQLAlchemy.

A DependentProfile represents a dependent linked to a caregiver (family member) 
and their own user account. Each dependent can have optional care notes.

Fields:
- dependent_id: Primary key for the dependent profile
- user_id: Foreign key linking to the dependent's User account (one-to-one)
- care_notes: Optional text notes about the dependent
- created_by: Foreign key linking to the caregiver who created the profile

Relationships:
- user: One-to-one relationship with the dependent's User account
- family_member: Many-to-one relationship with the caregiver (creator)
"""

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

# ---------------------------
# Local App Imports
# ---------------------------
from app.core.database import Base


# ---------------------------
# DependentProfile Model
# ---------------------------
class DependentProfile(Base):
    """
    SQLAlchemy model representing a dependent profile.

    Each dependent profile is linked to a unique User (dependent) and a 
    caregiver (family member) who created it.
    """

    __tablename__ = "dependent_profiles"

    # Primary key for dependent profile
    dependent_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Primary key for the dependent profile"
    )

    # One-to-one link to the dependent's user account
    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        unique=True,
        doc="User ID of the dependent; one-to-one relationship"
    )

    # Optional care notes for the dependent
    care_notes = Column(
        Text,
        nullable=True,
        doc="Optional care notes about the dependent"
    )

    # User ID of the caregiver who created this dependent profile
    created_by = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=True,
        doc="User ID of the caregiver (family member) who created the dependent profile"
    )

    # ---------------------------
    # Relationships
    # ---------------------------

    # Dependent's own user account
    user = relationship(
        "User",
        back_populates="dependent_profile",
        foreign_keys=[user_id],
        doc="One-to-one relationship to the dependent's User account"
    )

    # Family member (caregiver) who created this dependent profile
    family_member = relationship(
        "User",
        back_populates="dependents",
        foreign_keys=[created_by],
        doc="Many-to-one relationship to the caregiver (family member) who created the profile"
    )