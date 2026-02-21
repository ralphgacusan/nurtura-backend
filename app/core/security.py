"""
core/security.py

This module provides security-related utilities for the application, including:
- Password hashing and verification
- Access and refresh token creation and decoding
- Token hashing for secure storage

It uses JWT for authentication tokens and pwdlib for secure password hashing.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timedelta, timezone  # for token expiration and timestamps
import hashlib  # for hashing tokens

# ---------------------------
# Third-Party Imports
# ---------------------------
import jwt  # JSON Web Token encoding/decoding
from jwt.exceptions import InvalidTokenError  # handle invalid JWTs
from pwdlib import PasswordHash  # secure password hashing

# ---------------------------
# Local Application Imports
# ---------------------------
from app.core.config import settings  # project config
from app.models.user import User  # User model for token payload
from app.core.exceptions import credentials_exception  # common exception for invalid auth

# ---------------------------
# Configuration / Constants
# ---------------------------
ACCESS_SECRET_KEY = settings.ACCESS_SECRET_KEY  # secret for access tokens
REFRESH_SECRET_KEY = settings.REFRESH_SECRET_KEY  # secret for refresh tokens
ALGORITHM = settings.ALGORITHM  # JWT algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# Password hashing utility
password_hash = PasswordHash.recommended()  # recommended hashing algorithm from pwdlib
DUMMY_HASH = password_hash.hash("dummypassword")  # dummy hash for timing attack mitigation

# ---------------------------
# Password Utilities
# ---------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.
    """
    return password_hash.verify(plain_password, hashed_password)  # returns True/False


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using a secure algorithm.
    """
    return password_hash.hash(password)  # returns hashed string

# ---------------------------
# Token Hashing Utilities
# ---------------------------
def get_token_hash(token: str) -> str:
    """
    Returns SHA256 hash of the token to store in DB.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token(token: str, hashed_token: str) -> bool:
    """
    Verify a token against its stored hash.
    """
    return get_token_hash(token) == hashed_token  # True if matches, else False

# ---------------------------
# Access Token Utilities
# ---------------------------
def create_access_token(user: User, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user (User): The user object to encode into the token.
        expires_delta (timedelta | None): Optional custom expiration time.

    Returns:
        str: Encoded JWT access token.
    """
    # payload with essential user info
    to_encode = {
        "sub": str(user.user_id),
        "username": user.username,
        "role": user.role.value,
        "status": user.status.value,
    }

    # set expiration
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # add standard JWT fields
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    })

    # encode token
    return jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    """
    Decode a JWT access token and return the user ID.

    Raises:
        credentials_exception: If token is invalid or missing required data.

    Returns:
        str: User ID extracted from token.
    """
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception  # required field missing
        return user_id
    except InvalidTokenError:
        raise credentials_exception  # invalid signature or expired

# ---------------------------
# Refresh Token Utilities
# ---------------------------
def create_refresh_token(user: User, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT refresh token for a user.

    Args:
        user (User): The user object to encode into the token.
        expires_delta (timedelta | None): Optional custom expiration time.

    Returns:
        str: Encoded JWT refresh token.
    """
    to_encode = {
        "sub": str(user.user_id),
        "username": user.username,
        "role": user.role.value,
        "status": user.status.value,
    }

    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    })

    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def decode_refresh_token(token: str) -> dict:
    """
    Decode a JWT refresh token and validate its type.

    Raises:
        credentials_exception: If token is invalid or not a refresh token.

    Returns:
        dict: Payload extracted from the refresh token.
    """
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception  # token is not a refresh token
        return payload
    except InvalidTokenError:
        raise credentials_exception  # invalid signature or expired