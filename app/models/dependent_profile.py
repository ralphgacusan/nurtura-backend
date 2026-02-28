"""
models/dependent_profile.py

This module defines the DependentProfile ORM model for SQLAlchemy.
It represents a dependent profile linked to a user (dependent) and a caregiver (creator).

Fields:
- dependent_id: Primary key for the dependent profile
- user_id: Foreign key linking to the dependent's user account (unique, one-to-one)
- care_notes: Optional text notes about the dependent
- created_by: Foreign key linking to the caregiver who created the profile

Relationships:
- user: One-to-one relationship with the dependent's User account
- caregiver: Many-to-one relationship with the caregiver User
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
    __tablename__ = "dependent_profiles"

    # Primary key for dependent profile
    dependent_id = Column(Integer, primary_key=True, index=True)

    # One-to-one link to dependent's user account
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)

    # Optional care notes for the dependent
    care_notes = Column(Text, nullable=True)

    # User ID of the caregiver who created this dependent profile
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    # ---------------------------
    # Relationships
    # ---------------------------

    # Dependent's own user account
    user = relationship(
        "User",
        back_populates="dependent_profile",
        foreign_keys=[user_id]
    )

    # Caregiver who created this dependent
    caregiver = relationship(
        "User",
        back_populates="dependents",
        foreign_keys=[created_by]
    )