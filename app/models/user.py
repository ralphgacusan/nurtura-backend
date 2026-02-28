"""
models/user.py

Defines the User SQLAlchemy model and associated enums.
Users are the main actors in the system with roles, statuses,
and linked refresh tokens for authentication.

Fields:
- user_id: Primary key.
- first_name: User's first name.
- middle_name: Optional middle name.
- last_name: User's last name.
- username: Unique username.
- email: Optional unique email address.
- password_hash: Hashed password.
- role: UserRole enum.
- sex: Sex enum.
- birthdate: Optional birth date.
- phone_number: Optional phone number.
- status: UserStatus enum.
- created_at: Timestamp of account creation.
- updated_at: Timestamp of last update.

Relationships:
- refresh_tokens: One-to-many with RefreshToken (user sessions).
- dependent_profile: One-to-one with DependentProfile (for dependent users).
- dependents: One-to-many with DependentProfile (for caregiver users).
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone
import enum

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, String, Enum, DateTime, Date
from sqlalchemy.orm import relationship
from app.core.database import Base

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
    SQLAlchemy model representing a system user.

    Attributes:
        user_id (int): Primary key.
        first_name (str): User's first name.
        middle_name (str | None): Optional middle name.
        last_name (str): User's last name.
        username (str): Unique username.
        email (str | None): Unique email address.
        password_hash (str): Hashed password.
        role (UserRole): Role of the user.
        sex (Sex): Sex/gender of the user.
        birthdate (date | None): Optional birth date.
        phone_number (str | None): Optional phone number.
        status (UserStatus): Account status.
        created_at (datetime): Timestamp of account creation.
        updated_at (datetime): Timestamp of last update.
        refresh_tokens (list[RefreshToken]): Linked refresh tokens.
        dependent_profile (DependentProfile | None): Linked dependent profile (for dependent users).
        dependents (list[DependentProfile]): Dependent profiles created by caregiver users.
    """

    __tablename__ = "users"

    # ---------------------------
    # Columns
    # ---------------------------
    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=True, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    sex = Column(Enum(Sex), nullable=False)
    birthdate = Column(Date, nullable=True)
    phone_number = Column(String(20), nullable=True)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.active)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ---------------------------
    # Relationships
    # ---------------------------

    # One-to-many: user -> refresh tokens
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # One-to-one: dependent user -> dependent profile
    dependent_profile = relationship(
        "DependentProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        foreign_keys="[DependentProfile.user_id]"
    )

    # One-to-many: caregiver -> dependent profiles
    dependents = relationship(
        "DependentProfile",
        back_populates="caregiver",
        foreign_keys="[DependentProfile.created_by]"
    )