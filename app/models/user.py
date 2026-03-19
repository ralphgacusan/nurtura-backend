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
- created_care_spaces: One-to-many with CareSpace (as creator).
- care_space_memberships: One-to-many with CareSpaceMember (as member).
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone, date
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
    family_member = "family_member"

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
        email (str | None): Optional unique email address.
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
        created_care_spaces (list[CareSpace]): Care spaces created by this user.
        care_space_memberships (list[CareSpaceMember]): Memberships in care spaces.
        tasks (list[Task]): Task created.
    """

    __tablename__ = "users"

    # ---------------------------
    # Columns
    # ---------------------------
    user_id = Column(Integer, primary_key=True, index=True, doc="Primary key for the user")
    first_name = Column(String(50), nullable=False, doc="First name of the user")
    middle_name = Column(String(50), nullable=True, doc="Optional middle name")
    last_name = Column(String(50), nullable=False, doc="Last name of the user")
    username = Column(String(50), nullable=False, unique=True, index=True, doc="Unique username")
    email = Column(String(100), nullable=True, unique=True, index=True, doc="Optional unique email address")
    password_hash = Column(String(255), nullable=False, doc="Hashed password for authentication")
    role = Column(Enum(UserRole), nullable=False, doc="Role of the user in the system")
    sex = Column(Enum(Sex), nullable=False, doc="Sex/gender of the user")
    birthdate = Column(Date, nullable=True, doc="Optional birthdate of the user")
    phone_number = Column(String(20), nullable=True, doc="Optional phone number")
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.active, doc="Account status")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), doc="Account creation timestamp")
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        doc="Timestamp of last update"
    )

    # ---------------------------
    # Relationships
    # ---------------------------

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="One-to-many relationship with refresh tokens"
    )

    dependent_profile = relationship(
        "DependentProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        foreign_keys="[DependentProfile.user_id]",
        doc="One-to-one relationship with dependent profile (for dependent users)"
    )

    dependents = relationship(
        "DependentProfile",
        back_populates="family_member",
        foreign_keys="[DependentProfile.created_by]",
        doc="One-to-many relationship to dependent profiles created by caregiver users"
    )

    created_care_spaces = relationship(
        "CareSpace",
        back_populates="creator",
        doc="One-to-many relationship to care spaces created by this user"
    )

    care_space_memberships = relationship(
        "CareSpaceMember",
        back_populates="user",
        doc="One-to-many relationship to care space memberships (as caregiver/member)"
    )

    created_tasks = relationship(
        "Task",
        back_populates="creator",
        doc="One-to-many relationship to tasks created by this user"
    )

    task_assignments = relationship(
        "TaskAssignment",
        back_populates="user",
        doc="One-to-many relationship to assigned tasks"
    )

    chatbot_history = relationship(
        "ChatbotHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="All AI interactions associated with this user"
    )