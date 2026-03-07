"""
core/security.py

This module provides security-related utilities for the application, including:
- Password hashing and verification
- Access and refresh token creation and decoding
- Token hashing for secure storage
- Join code hashing and verification

It uses JWT for authentication tokens and pwdlib for secure password hashing.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timedelta, timezone  # for token expiration and timestamps
import hashlib  # for hashing tokens and join codes

# ---------------------------
# Third-Party Imports
# ---------------------------
import jwt  # JSON Web Token encoding/decoding
from jwt.exceptions import InvalidTokenError  # handle invalid JWTs
from pwdlib import PasswordHash  # secure password hashing

# ---------------------------
# Local Application Imports
# ---------------------------
from app.core.config import settings  # project configuration
from app.models.user import User  # User model for token payload
from app.core.exceptions import credentials_exception  # common exception for invalid auth

# ---------------------------
# Configuration / Constants
# ---------------------------
ACCESS_SECRET_KEY = settings.ACCESS_SECRET_KEY  # secret key for signing access tokens
REFRESH_SECRET_KEY = settings.REFRESH_SECRET_KEY  # secret key for signing refresh tokens
ALGORITHM = settings.ALGORITHM  # JWT signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES  # access token lifetime
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS  # refresh token lifetime

# Password hashing utility
password_hash = PasswordHash.recommended()  # recommended hashing algorithm from pwdlib
DUMMY_HASH = password_hash.hash("dummypassword")  # dummy hash for timing attack mitigation

# ---------------------------
# Password Utilities
# ---------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Args:
        plain_password (str): The user's input password.
        hashed_password (str): The securely hashed password stored in the database.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using a secure algorithm.

    Args:
        password (str): The plaintext password.

    Returns:
        str: Hashed password ready for secure storage.
    """
    return password_hash.hash(password)

# ---------------------------
# Token Hashing Utilities
# ---------------------------
def get_token_hash(token: str) -> str:
    """
    Returns SHA256 hash of a token for secure database storage.

    Args:
        token (str): The plaintext token.

    Returns:
        str: SHA256 hashed token.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token(token: str, hashed_token: str) -> bool:
    """
    Verify a token against its stored hash.

    Args:
        token (str): The plaintext token.
        hashed_token (str): The stored hashed token.

    Returns:
        bool: True if the token matches the hash, False otherwise.
    """
    return get_token_hash(token) == hashed_token

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

    # add standard JWT claims
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

    Args:
        token (str): JWT access token.

    Returns:
        str: User ID extracted from token payload.
    """
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except InvalidTokenError:
        raise credentials_exception

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

    Args:
        token (str): JWT refresh token.

    Returns:
        dict: Payload extracted from the refresh token.
    """
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception
        return payload
    except InvalidTokenError:
        raise credentials_exception

# ---------------------------
# Join Code Utilities
# ---------------------------
def hash_join_code(code: str) -> str:
    """
    Hash a join code using SHA256 for secure storage.

    Args:
        code (str): Plain join code.

    Returns:
        str: SHA256 hashed join code.
    """
    return hashlib.sha256(code.encode()).hexdigest()


def verify_join_code(code: str, hashed_code: str) -> bool:
    """
    Verify a join code against its stored hash.

    Args:
        code (str): Plain join code.
        hashed_code (str): Stored hashed join code.

    Returns:
        bool: True if the code matches, False otherwise.
    """
    return hash_join_code(code) == hashed_code