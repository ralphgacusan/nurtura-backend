"""
schemas/user.py

Pydantic schemas for User operations.
Includes creation, login, reading, updating, and password change.

Features:
- Base user schema
- User creation with password validation
- Login schema
- Read and update schemas
- Password change schema
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, date
import re  # For password strength validation

# ---------------------------
# Pydantic Imports
# ---------------------------
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated, Optional

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
def validate_birthdate_not_future(value: Optional[date]) -> Optional[date]:
    """Raise ValueError if birthdate is in the future."""
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
# BASE USER SCHEMA
# ---------------------------
class UserBase(BaseModel):
    """
    Base schema shared by user creation, read, and update schemas.

    Attributes:
        first_name (str): Required first name (1-50 chars, letters only)
        middle_name (str | None): Optional middle name (max 50 chars)
        last_name (str): Required last name (1-50 chars)
        username (str): Unique username (3-50 chars, letters/numbers/underscores)
        email (EmailStr | None): Optional email
        role (UserRole): User role (family_member/caregiver/dependent)
        sex (Sex): Sex/gender
        birthdate (date | None): Optional; cannot be in future
        phone_number (str | None): Optional phone number (international format)
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
    role: UserRole
    sex: Sex
    birthdate: Optional[date] = None
    phone_number: Annotated[Optional[str], Field(pattern=r"^\+?\d{7,20}$")] = None

    @field_validator("birthdate")
    @classmethod
    def validate_birthdate(cls, birthdate_value: Optional[date]) -> Optional[date]:
        """Ensure birthdate is not in the future."""
        return validate_birthdate_not_future(birthdate_value)

    @field_validator("middle_name", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        if v == "":
            return None
        return v

# ---------------------------
# LOGIN SCHEMA
# ---------------------------
class UserLogin(BaseModel):
    """
    Schema for user login requests.

    Attributes:
        username (str): Login username
        password (str): Login password
    """
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=8)]

# ---------------------------
# USER CREATION SCHEMA
# ---------------------------
class UserCreate(UserBase):
    """
    Schema for creating a new user with password validation.

    Attributes:
        password (str): Required password (8-128 chars, must meet strength criteria)
    """
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("password")
    @classmethod
    def password_strength(cls, password_value: str) -> str:
        return validate_password_strength(password_value)

# ---------------------------
# USER READ SCHEMA
# ---------------------------
class UserRead(UserBase):
    """
    Schema for reading user information.

    Attributes:
        user_id (int): Primary key
        status (UserStatus): Current account status
        created_at (datetime): Timestamp of creation
        updated_at (datetime): Timestamp of last update
    """
    user_id: int
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM mode
    }

# ---------------------------
# USER UPDATE SCHEMA
# ---------------------------
class UserUpdate(BaseModel):
    """
    Schema for updating user information (PATCH-style).

    All fields are optional.

    Attributes:
        first_name (str | None)
        middle_name (str | None)
        last_name (str | None)
        username (str | None)
        email (EmailStr | None)
        sex (Sex | None)
        birthdate (date | None)
        phone_number (str | None)
    """
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
        """Ensure birthdate is not in the future."""
        return validate_birthdate_not_future(birthdate_value)

    @field_validator("middle_name", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        if v == "":
            return None
        return v

# ---------------------------
# PASSWORD CHANGE SCHEMA
# ---------------------------
class PasswordChange(BaseModel):
    """
    Schema for changing a user's password.

    Attributes:
        current_password (str): Current password for verification
        new_password (str): New password (8-128 chars, must meet strength criteria)
    """
    current_password: str
    new_password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, new_password: str) -> str:
        return validate_password_strength(new_password)