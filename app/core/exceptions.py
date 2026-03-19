"""
core/exceptions.py

This module defines reusable HTTP exceptions for the FastAPI application.

All exceptions inherit from FastAPI's HTTPException and are categorized into:
- Authentication & authorization errors
- Resource errors
- Input validation errors
- Dependent profile errors
- CareSpace errors
- CareSpace member & dependent errors
- CareSpace join code errors

Usage Example:
    from app.core.exceptions import invalid_credentials_exception
    raise invalid_credentials_exception
"""

from fastapi import HTTPException, status  # HTTPException class and standard HTTP status codes

# ---------------------------
# Authentication & Authorization Errors
# ---------------------------

# Raised when credentials cannot be validated (generic fallback for OAuth2)
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,  # HTTP 401 Unauthorized
    detail="Could not validate credentials",   # Message returned in response
    headers={"WWW-Authenticate": "Bearer"},   # Required for OAuth2 Bearer token flow
)

# Raised when username or password is incorrect during login
invalid_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

# Raised when a user exists but is inactive and cannot log in
inactive_user_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,  # HTTP 400 Bad Request
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

# Raised when input validation fails (e.g., Pydantic schema validation errors)
invalid_input_exception = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,  # HTTP 422 Unprocessable Entity
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
    status_code=status.HTTP_403_FORBIDDEN,  # HTTP 403 Forbidden
    detail="You do not have permission to perform this action"
)

# ---------------------------
# CareSpace Errors
# ---------------------------

# Raised when a requested care space does not exist
care_space_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Care space not found"
)

# Raised when attempting to create or update a care space with a code that already exists
care_space_code_already_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Care space code already exists"
)

# ---------------------------
# CareSpace Member & Dependent Errors
# ---------------------------

# Raised when a care space member is not found
care_space_member_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Care space member not found"
)

# Raised when a care space dependent assignment is not found
care_space_dependent_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Care space dependent assignment not found"
)

# ---------------------------
# CareSpace Join Code Errors
# ---------------------------

# Raised when the maximum number of active join codes for a care space is reached
too_many_active_join_codes_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Too many active join codes for this care space"
)

# Raised when a provided join code is invalid (not found in DB)
invalid_join_code_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Invalid join code"
)

# Raised when a join code has expired
join_code_expired_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Join code has expired"
)

# Raised when a join code has already been used
join_code_already_used_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Join code has already been used"
)

# Raised when a user is already a member of the care space
already_member_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User is already a member of this care space"
)

# ---------------------------
# Task Errors
# ---------------------------

# Raised when a task cannot be created for some reason
task_creation_failed_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Failed to create task"
)

# Raised when creating an assignment fails
task_assignment_creation_failed_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Failed to create task assignment"
)

# Raised when creating a schedule fails
task_schedule_creation_failed_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Failed to create task schedule"
)

# Raised when creating a completion fails
task_completion_creation_failed_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Failed to create task completion"
)


# Task update failed
task_update_failed_exception = HTTPException(
    status_code=500,
    detail="Failed to update task status"
)

# Task completion not found
task_completion_not_found_exception = HTTPException(
    status_code=404,
    detail="Task completion not found"
)

# Task assignment not found
task_assignment_not_found_exception = HTTPException(
    status_code=404,
    detail="Task assignment not found"
)
