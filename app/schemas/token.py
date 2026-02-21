"""
schemas/token.py

This module defines Pydantic schemas for authentication tokens
and refresh token operations.

Features:
- Access & refresh token response models
- Token data for decoding JWTs
- Refresh token creation and request schemas
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime  # for token expiration timestamps

# ---------------------------
# Pydantic Imports
# ---------------------------
from pydantic import BaseModel  # base class for Pydantic schemas

# ---------------------------
# Local App Imports
# ---------------------------
from app.models.user import UserRole, UserStatus  # enums for roles and user status

# ---------------------------
# Token Schemas
# ---------------------------
class Token(BaseModel):
    """
    Response schema for access and refresh tokens returned by the API.
    Used for login and refresh endpoints.
    """
    access_token: str  # JWT access token string
    refresh_token: str  # JWT refresh token string
    token_type: str = "bearer"  # token type (default is bearer)
    username: str  # username of the authenticated user
    role: str      # role of the authenticated user (admin/caregiver/dependent)


class TokenData(BaseModel):
    """
    Schema representing data extracted from a decoded JWT.
    Used internally to validate and store token payload info.
    """
    user_id: int        # ID of the user
    username: str       # username from token
    role: UserRole      # role extracted from token
    status: UserStatus  # status of the user account


# ---------------------------
# Refresh Token Schemas
# ---------------------------
class RefreshTokenBase(BaseModel):
    """
    Base schema for refresh token fields that are common across requests.
    Includes optional device and IP information.
    """
    device_info: str | None = None  # optional client device info
    ip_address: str | None = None   # optional client IP address


class RefreshTokenCreate(RefreshTokenBase):
    """
    Schema used when creating a refresh token in the database.
    Extends RefreshTokenBase with user ID, token hash, and expiration date.
    """
    user_id: int         # ID of the user this refresh token belongs to
    token_hash: str      # SHA256 hash of the refresh token
    expires_at: datetime # expiration datetime of the token


class RefreshTokenRequest(BaseModel):
    """
    Schema for requests where the client sends a refresh token.
    Used for token refresh and logout endpoints.
    """
    refresh_token: str  # the raw refresh token string sent by client