"""
models/user.py

Defines the User SQLAlchemy model and associated enums.
Users are the main actors in the system with roles, statuses,
and linked refresh tokens for authentication.

Relationships:
    - One-to-many with RefreshToken: a user can have multiple refresh tokens.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone  # for timestamps
import enum  # for user enums

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship  # for model relationships
from app.core.database import Base  # declarative base

# ---------------------------
# User Enums
# ---------------------------
class UserRole(str, enum.Enum):
    """User roles in the system."""
    caregiver = "caregiver"
    dependent = "dependent"
    admin = "admin"

class Sex(str, enum.Enum):
    """Sex/gender of the user."""
    male = "male"
    female = "female"
    other = "other"

class UserStatus(str, enum.Enum):
    """User account status."""
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    deactivated = "deactivated"

# ---------------------------
# User Model
# ---------------------------
class User(Base):
    """
    SQLAlchemy model for users.

    Attributes:
        user_id (int): Primary key.
        first_name (str): User's first name.
        middle_name (str | None): Optional middle name.
        last_name (str): User's last name.
        username (str): Unique username.
        email (str): Unique email address.
        password_hash (str): Hashed password.
        role (UserRole): Role of the user.
        sex (Sex): Sex/gender of the user.
        phone_number (str | None): Optional phone number.
        status (UserStatus): Account status.
        created_at (datetime): Account creation timestamp.
        updated_at (datetime): Last update timestamp.
        refresh_tokens (list[RefreshToken]): Linked refresh tokens.
    """

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)  # primary key
    first_name = Column(String(50), nullable=False)  # first name
    middle_name = Column(String(50), nullable=True)  # optional middle name
    last_name = Column(String(50), nullable=False)  # last name
    username = Column(String(50), nullable=False, unique=True, index=True)  # unique username
    email = Column(String(100), nullable=False, unique=True, index=True)  # unique email
    password_hash = Column(String(255), nullable=False)  # hashed password
    role = Column(Enum(UserRole), nullable=False)  # role enum
    sex = Column(Enum(Sex), nullable=False)  # sex enum
    phone_number = Column(String(20), nullable=True)  # optional phone
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.active)  # account status
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  # creation timestamp
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),  # auto-update on modification
    )

    # One-to-many relationship to refresh tokens
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",  # matches `user` in RefreshToken model
        cascade="all, delete-orphan"  # remove refresh tokens if user is deleted
    )