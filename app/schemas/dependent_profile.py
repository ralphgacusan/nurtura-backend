"""
schemas/dependent_profile.py

This module defines Pydantic schemas for managing DependentProfile data.
It provides validation, creation, reading, updating, and password change schemas.

Features:
- Base schema for shared fields
- Schemas for creating dependent users and profiles
- Schemas for reading dependent profiles with optional nested user info
- Schemas for updating dependent profiles (PATCH-style)
- Password validation and change schemas
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import date
import re  # for password strength validation

# ---------------------------
# Pydantic Imports
# ---------------------------
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated

# ---------------------------
# Local App Imports
# ---------------------------
from app.models.user import Sex, UserRole
from app.schemas.user import UserRead  # optional nested user info

# ---------------------------
# Shared Validation Functions
# ---------------------------
def validate_birthdate_not_future(value: date | None) -> date | None:
    """Raise error if birthdate is in the future."""
    if value and value > date.today():
        raise ValueError("Birthdate cannot be in the future")
    return value

def validate_password_strength(value: str) -> str:
    """Validate that password contains uppercase, lowercase, and special character."""
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
# Base DependentProfile Schema
# ---------------------------
class DependentProfileBase(BaseModel):
    """
    Shared fields for DependentProfile schemas.

    Fields:
        care_notes (str | None): Optional notes about the dependent, max 500 chars.
    """
    care_notes: Annotated[str | None, Field(max_length=500)] = None

# ---------------------------
# DependentProfile Creation Schema
# ---------------------------
class DependentProfileCreate(DependentProfileBase):
    """
    Schema for creating a dependent user and profile.

    Fields:
        first_name (str): Required first name, max 50 chars.
        middle_name (str | None): Optional middle name, max 50 chars.
        last_name (str): Required last name, max 50 chars.
        username (str): Unique username, 3-50 chars, letters/numbers/underscores.
        email (EmailStr | None): Optional unique email.
        role (UserRole): User role, default 'dependent'.
        sex (Sex): Sex/gender of the dependent.
        birthdate (date | None): Optional birthdate; cannot be in the future.
        phone_number (str | None): Optional phone in international format.
        password (str): Required password, 8-128 chars; must meet strength criteria.
    """
    first_name: Annotated[
        str, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)
    ]
    middle_name: Annotated[
        str | None, Field(max_length=50, pattern=name_regex, strip_whitespace=True)
    ] = None
    last_name: Annotated[
        str, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)
    ]
    username: Annotated[
        str, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    ]
    email: EmailStr | None = None
    role: UserRole = UserRole.dependent
    sex: Sex
    birthdate: date | None = None
    phone_number: Annotated[str | None, Field(pattern=r"^\+?\d{7,20}$")] = None
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("birthdate")
    @classmethod
    def validate_birthdate(cls, birthdate_value: date | None) -> date | None:
        return validate_birthdate_not_future(birthdate_value)

    @field_validator("password")
    @classmethod
    def password_strength(cls, password_value: str) -> str:
        return validate_password_strength(password_value)

# ---------------------------
# DependentProfile Store Schema
# ---------------------------
class DependentProfileStore(DependentProfileBase):
    """
    Schema for creating a dependent profile for an existing user.

    Fields:
        user_id (int): FK to the User table.
        created_by (int): User ID of the caregiver creating the profile.
    """
    user_id: int
    created_by: int

# ---------------------------
# DependentProfile Read Schema
# ---------------------------
class DependentProfileRead(DependentProfileBase):
    """
    Schema for reading dependent profiles.

    Fields:
        dependent_id (int): Primary key of the dependent profile.
        user_id (int): FK to the dependent's user account.
        user (UserRead | None): Optional nested user information.
        created_by (int): User ID of the caregiver who created the profile.
    """
    dependent_id: int
    user_id: int
    user: UserRead | None = None
    created_by: int

    model_config = {
        "from_attributes": True  # ORM mode for SQLAlchemy
    }

# ---------------------------
# DependentProfile Update Schema
# ---------------------------
class DependentProfileUpdate(BaseModel):
    """
    Schema for updating dependent profiles and related user fields.

    All fields optional (PATCH-style).

    Fields:
        care_notes (str | None): Optional care notes.
        first_name (str | None)
        middle_name (str | None)
        last_name (str | None)
        username (str | None)
        email (EmailStr | None)
        sex (Sex | None)
        birthdate (date | None)
        phone_number (str | None)
    """
    care_notes: Annotated[str | None, Field(max_length=500)] = None
    first_name: Annotated[str | None, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)] = None
    middle_name: Annotated[str | None, Field(max_length=50, pattern=name_regex, strip_whitespace=True)] = None
    last_name: Annotated[str | None, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)] = None
    username: Annotated[str | None, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")] = None
    email: EmailStr | None = None
    sex: Sex | None = None
    birthdate: date | None = None
    phone_number: Annotated[str | None, Field(pattern=r"^\+?\d{7,20}$")] = None

    @field_validator("birthdate")
    @classmethod
    def validate_birthdate(cls, birthdate_value: date | None) -> date | None:
        return validate_birthdate_not_future(birthdate_value)

# ---------------------------
# Dependent Password Change Schema
# ---------------------------
class DependentPasswordChange(BaseModel):
    """
    Schema for changing a dependent's password.

    Fields:
        old_password (str): Current password.
        new_password (str): New password (min 8 chars, must include uppercase, lowercase, special character).
    """
    old_password: str
    new_password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, new_password: str) -> str:
        return validate_password_strength(new_password)