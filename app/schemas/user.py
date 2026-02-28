"""
schemas/user.py

This module defines Pydantic schemas for User-related operations.

Features:
- Base user schema for shared fields
- User creation with strong password validation
- User login schema
- User read and update schemas
- Password change schema
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, date
import re  # for password strength validation

# ---------------------------
# Pydantic Imports
# ---------------------------
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated

# ---------------------------
# Local App Imports
# ---------------------------
from app.models.user import Sex, UserRole, UserStatus

# ---------------------------
# Constants
# ---------------------------
name_regex = r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$"  # letters, spaces, hyphens, apostrophes only

# ---------------------------
# Shared Validation Functions
# ---------------------------
def validate_birthdate_not_future(value: date | None) -> date | None:
    """Raise ValueError if birthdate is in the future."""
    if value and value > date.today():
        raise ValueError("Birthdate cannot be in the future")
    return value

def validate_password_strength(value: str) -> str:
    """Validate password strength: must include uppercase, lowercase, special character."""
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise ValueError("Password must contain at least one special character")
    return value

# ---------------------------
# Base User Schema
# ---------------------------
class UserBase(BaseModel):
    """
    Base schema shared by user creation, read, and update schemas.

    Fields:
        first_name (str): Required first name (1-50 chars, letters only)
        middle_name (str | None): Optional middle name (max 50 chars)
        last_name (str): Required last name (1-50 chars)
        username (str): Unique username (3-50 chars, letters/numbers/underscores)
        email (EmailStr | None): Optional email address
        role (UserRole): Role of the user (admin/caregiver/dependent)
        sex (Sex): Sex/gender of the user
        birthdate (date | None): Optional birthdate (cannot be in future)
        phone_number (str | None): Optional phone number (international format)
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
    role: UserRole
    sex: Sex
    birthdate: date | None = None
    phone_number: Annotated[str | None, Field(pattern=r"^\+?\d{7,20}$")] = None

    @field_validator("birthdate")
    @classmethod
    def validate_birthdate(cls, birthdate_value: date | None) -> date | None:
        """Ensure birthdate is not in the future."""
        return validate_birthdate_not_future(birthdate_value)

# ---------------------------
# Login Schema
# ---------------------------
class UserLogin(BaseModel):
    """
    Schema for user login requests.

    Fields:
        username (str): Login username
        password (str): Login password
    """
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=8)]

# ---------------------------
# User Creation Schema
# ---------------------------
class UserCreate(UserBase):
    """
    Schema for creating a new user with password validation.

    Fields:
        password (str): Required password (8-128 chars, must meet strength criteria)
    """
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("password")
    @classmethod
    def password_strength(cls, password_value: str) -> str:
        return validate_password_strength(password_value)

# ---------------------------
# User Read Schema
# ---------------------------
class UserRead(UserBase):
    """
    Schema for reading user information.

    Fields:
        user_id (int): Primary key
        status (UserStatus): Current account status
        created_at (datetime): Timestamp of account creation
        updated_at (datetime): Timestamp of last update
    """
    user_id: int
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # ORM mode
    }

# ---------------------------
# User Update Schema
# ---------------------------
class UserUpdate(BaseModel):
    """
    Schema for updating user information (PATCH-style).

    All fields are optional.

    Fields:
        first_name (str | None)
        middle_name (str | None)
        last_name (str | None)
        username (str | None)
        email (EmailStr | None)
        sex (Sex | None)
        phone_number (str | None)
    """
    first_name: Annotated[str | None, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)] = None
    middle_name: Annotated[str | None, Field(max_length=50, pattern=name_regex, strip_whitespace=True)] = None
    last_name: Annotated[str | None, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)] = None
    username: Annotated[str | None, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")] = None
    email: EmailStr | None = None
    sex: Sex | None = None
    phone_number: Annotated[str | None, Field(pattern=r"^\+?\d{7,20}$")] = None

# ---------------------------
# Password Change Schema
# ---------------------------
class PasswordChange(BaseModel):
    """
    Schema for changing a user's password.

    Fields:
        current_password (str): Current password for verification
        new_password (str): New password (8-128 chars, must meet strength criteria)
    """
    current_password: str
    new_password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, new_password: str) -> str:
        return validate_password_strength(new_password)