"""
schemas/dependent_profile.py

Pydantic schemas for DependentProfile.
Handles creation, reading, updating, and password change validation.

Features:
- Base schema with shared fields
- Create schemas for new dependent users and profiles
- Read schema with optional nested user info
- Update schema (PATCH-style)
- Password change validation schema
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import date
import re  # For password strength validation

# ---------------------------
# Pydantic Imports
# ---------------------------
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated, Optional

# ---------------------------
# Local App Imports
# ---------------------------
from app.models.user import Sex, UserRole
from app.schemas.user import UserRead  # optional nested user info

# ---------------------------
# Shared Validation Functions
# ---------------------------
def validate_birthdate_not_future(value: Optional[date]) -> Optional[date]:
    """Raise error if birthdate is in the future."""
    if value and value > date.today():
        raise ValueError("Birthdate cannot be in the future")
    return value

def validate_password_strength(value: str) -> str:
    """Ensure password contains uppercase, lowercase, and special character."""
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise ValueError("Password must contain at least one special character")
    return value

# ---------------------------
# Constants
# ---------------------------
name_regex = r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$"  # letters, spaces, hyphens, apostrophes only

# ---------------------------
# BASE SCHEMA
# ---------------------------
class DependentProfileBase(BaseModel):
    """
    Shared fields for DependentProfile schemas.

    Attributes:
        care_notes (str | None): Optional notes about the dependent, max 500 chars.
    """
    care_notes: Annotated[Optional[str], Field(max_length=500)] = None

# ---------------------------
# CREATE SCHEMA (Dependent User + Profile)
# ---------------------------
class DependentProfileCreate(DependentProfileBase):
    """
    Schema for creating a dependent user and profile.

    Attributes:
        first_name (str): Required first name, max 50 chars.
        middle_name (str | None): Optional middle name, max 50 chars.
        last_name (str): Required last name, max 50 chars.
        username (str): Unique username, 3-50 chars, letters/numbers/underscores.
        email (EmailStr | None): Optional unique email.
        role (UserRole): Defaults to 'dependent'.
        sex (Sex): Sex/gender of the dependent.
        birthdate (date | None): Optional birthdate; cannot be in the future.
        phone_number (str | None): Optional phone in international format.
        password (str): Required password, 8-128 chars; must meet strength criteria.
    """
    first_name: Annotated[
        str, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)
    ]
    middle_name: Annotated[
        Optional[str], Field(max_length=50, pattern=name_regex, strip_whitespace=True)
    ] = None
    last_name: Annotated[
        str, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)
    ]
    username: Annotated[
        str, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    ]
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.dependent
    sex: Sex
    birthdate: Optional[date] = None
    phone_number: Annotated[Optional[str], Field(pattern=r"^\+?\d{7,20}$")] = None
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("middle_name", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        if v == "":
            return None
        return v

    @field_validator("birthdate")
    @classmethod
    def validate_birthdate(cls, birthdate_value: Optional[date]) -> Optional[date]:
        return validate_birthdate_not_future(birthdate_value)

    @field_validator("password")
    @classmethod
    def password_strength(cls, password_value: str) -> str:
        return validate_password_strength(password_value)

# ---------------------------
# STORE SCHEMA (Dependent Profile for Existing User)
# ---------------------------
class DependentProfileStore(DependentProfileBase):
    """
    Schema for creating a dependent profile for an existing user.

    Attributes:
        user_id (int): FK to the User table.
        created_by (int): User ID of the family member creating the profile.
    """
    user_id: int
    created_by: int

# ---------------------------
# READ SCHEMA
# ---------------------------
class DependentProfileRead(DependentProfileBase):
    """
    Schema for reading dependent profiles.

    Attributes:
        dependent_id (int): Primary key of the dependent profile.
        user_id (int): FK to the dependent's user account.
        user (UserRead | None): Optional nested user information.
        created_by (int): User ID of the family member who created the profile.
    """
    dependent_id: int
    user_id: int
    user: Optional[UserRead] = None
    created_by: int

    model_config = {
        "from_attributes": True  # Enables ORM mode for SQLAlchemy models
    }

# ---------------------------
# UPDATE SCHEMA
# ---------------------------
class DependentProfileUpdate(BaseModel):
    """
    Schema for updating dependent profiles and related user fields (PATCH-style).

    All fields are optional.
    """
    care_notes: Annotated[Optional[str], Field(max_length=500)] = None
    first_name: Annotated[Optional[str], Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)] = None
    middle_name: Annotated[Optional[str], Field(max_length=50, pattern=name_regex, strip_whitespace=True)] = None
    last_name: Annotated[Optional[str], Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)] = None
    username: Annotated[Optional[str], Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")] = None
    email: Optional[EmailStr] = None
    sex: Optional[Sex] = None
    birthdate: Optional[date] = None
    phone_number: Annotated[Optional[str], Field(pattern=r"^\+?\d{7,20}$")] = None

    @field_validator("birthdate")
    @classmethod
    def validate_birthdate(cls, birthdate_value: Optional[date]) -> Optional[date]:
        return validate_birthdate_not_future(birthdate_value)

# ---------------------------
# PASSWORD CHANGE SCHEMA
# ---------------------------
class DependentPasswordChange(BaseModel):
    """
    Schema for changing a dependent's password.

    Attributes:
        old_password (str): Current password.
        new_password (str): New password; must meet strength requirements.
    """
    old_password: str
    new_password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, new_password: str) -> str:
        return validate_password_strength(new_password)