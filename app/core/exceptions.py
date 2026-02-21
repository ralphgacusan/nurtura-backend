"""
core/exceptions.py

This module defines reusable HTTP exceptions for the FastAPI application.
All exceptions are based on FastAPI's HTTPException and
are categorized for authentication, resource, and validation errors.

Usage:
    from app.core.exceptions import invalid_credentials_exception
    raise invalid_credentials_exception
"""

from fastapi import HTTPException, status  # FastAPI HTTPException and standard status codes

# ---------------------------
# Authentication & Authorization Errors
# ---------------------------

# Raised when credentials could not be validated (generic fallback)
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,  # 401 Unauthorized HTTP status
    detail="Could not validate credentials",   # Message returned in response
    headers={"WWW-Authenticate": "Bearer"},   # Required for OAuth2 Bearer
)

# Raised when username or password is incorrect during login
invalid_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

# Raised when a user exists but is inactive and cannot log in
inactive_user_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,  # 400 Bad Request for invalid user status
    detail="Inactive user"
)

# Raised when a refresh token is invalid, expired, or revoked
invalid_refresh_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired refresh token"
)

# ---------------------------
# Resource Errors
# ---------------------------

# Raised when a requested user or resource does not exist
user_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,  # 404 Not Found HTTP status
    detail="User not found"
)

# Raised when attempting to register or update an email that already exists
email_already_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email is already registered"
)

# Raised when attempting to register or update a username that already exists
username_already_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Username is already taken"
)

# ---------------------------
# Input Validation Errors
# ---------------------------

# Raised when input validation fails (e.g., schema validation)
invalid_input_exception = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,  # 422 Unprocessable Entity for validation issues
    detail="Invalid input"
)