"""
schemas/user.py

This module defines Pydantic schemas for User-related operations.

Features:
- Base user fields
- User creation with strong password validation
- User login schema
- User update and read schemas
- Password change schema
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime  # for timestamps in UserRead
import re  # for password strength validation

# ---------------------------
# Pydantic Imports
# ---------------------------
from pydantic import BaseModel, EmailStr, Field, field_validator  # schema base, validation, field constraints
from typing import Annotated  # for type annotations with Pydantic Field metadata

# ---------------------------
# Local App Imports
# ---------------------------
from app.models.user import Sex, UserRole, UserStatus  # enums for user fields

# ---------------------------
# Constants
# ---------------------------
name_regex = r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$"  # letters, spaces, hyphens, apostrophes only

# ---------------------------
# Base User Schema
# ---------------------------
class UserBase(BaseModel):
    """
    Shared fields for all user-related schemas.
    Used as a base class for creation, reading, and update schemas.
    """
    first_name: Annotated[
        str, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)
    ]  # required first name
    middle_name: Annotated[
        str | None, Field(max_length=50, pattern=name_regex, strip_whitespace=True)
    ] = None  # optional middle name
    last_name: Annotated[
        str, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)
    ]  # required last name
    username: Annotated[
        str, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    ]  # unique username
    email: EmailStr  # validated email address
    role: UserRole  # role enum
    sex: Sex  # sex/gender enum
    phone_number: Annotated[
        str | None, Field(pattern=r"^\+?\d{7,20}$")
    ] = None  # optional phone number in international format

# ---------------------------
# Login Schema
# ---------------------------
class UserLogin(BaseModel):
    """
    Schema for user login request.
    """
    username: Annotated[str, Field(min_length=3, max_length=50)]  # login username
    password: Annotated[str, Field(min_length=8)]  # login password

# ---------------------------
# User Creation Schema
# ---------------------------
class UserCreate(UserBase):
    """
    Schema for creating a new user with password validation.
    Inherits all fields from UserBase.
    """
    password: Annotated[str, Field(min_length=8, max_length=128)]  # required password

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        Validate password strength: at least one uppercase, one lowercase, and one special character.
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

# ---------------------------
# User Read Schema
# ---------------------------
class UserRead(UserBase):
    """
    Schema returned when reading user information.
    Includes read-only fields like user_id, status, and timestamps.
    """
    user_id: int  # primary key
    status: UserStatus  # current status
    created_at: datetime  # creation timestamp
    updated_at: datetime  # last update timestamp

    model_config = {
        "from_attributes": True  # enables ORM mode for SQLAlchemy models
    }

# ---------------------------
# User Update Schema
# ---------------------------
class UserUpdate(BaseModel):
    """
    Schema for updating user information (partial update allowed).
    All fields are optional for PATCH-style updates.
    """
    first_name: Annotated[
        str | None, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)
    ] = None
    middle_name: Annotated[
        str | None, Field(max_length=50, pattern=name_regex, strip_whitespace=True)
    ] = None
    last_name: Annotated[
        str | None, Field(min_length=1, max_length=50, pattern=name_regex, strip_whitespace=True)
    ] = None
    username: Annotated[
        str | None, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    ] = None
    email: EmailStr | None = None
    sex: Sex | None = None
    phone_number: Annotated[str | None, Field(pattern=r"^\+?\d{7,20}$")] = None

# ---------------------------
# Password Change Schema
# ---------------------------
class PasswordChange(BaseModel):
    """
    Schema for changing the current user's password.
    """
    current_password: str  # current password for verification
    new_password: Annotated[str, Field(min_length=8, max_length=128)]  # new password

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        Validate new password strength (same rules as UserCreate).
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v