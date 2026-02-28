"""
core/exceptions.py

This module defines reusable HTTP exceptions for the FastAPI application.
All exceptions are based on FastAPI's HTTPException and
are categorized for authentication, resource, validation, and authorization errors.

Usage:
    from app.core.exceptions import invalid_credentials_exception
    raise invalid_credentials_exception
"""

from fastapi import HTTPException, status  # FastAPI HTTPException and standard status codes

# ---------------------------
# Authentication & Authorization Errors
# ---------------------------

# Raised when credentials cannot be validated (generic fallback for OAuth2)
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,  # Standard HTTP 401
    detail="Could not validate credentials",   # Error message returned
    headers={"WWW-Authenticate": "Bearer"},   # Required for OAuth2 Bearer token flow
)

# Raised when username or password is incorrect during login
invalid_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

# Raised when a user exists but is inactive (cannot log in)
inactive_user_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,  # Bad request for invalid status
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
    status_code=status.HTTP_404_NOT_FOUND,
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

# Raised when input validation fails (e.g., Pydantic schema validation)
invalid_input_exception = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Invalid input"
)

# ---------------------------
# Dependent Profile Errors
# ---------------------------

# Raised when a dependent profile is not found
dependent_profile_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Dependent profile not found"
)

# Raised when a user already has a dependent profile (one-to-one constraint)
user_already_has_dependent_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User already has a dependent profile"
)

# ---------------------------
# Authorization Errors
# ---------------------------

# Raised when a user is authenticated but not allowed to perform a specific action
forbidden_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You do not have permission to perform this action"
)