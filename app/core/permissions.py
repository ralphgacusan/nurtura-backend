"""
core/permissions.py

This module defines reusable permission checks for role-based access control.
Functions can be used across services or routers to enforce user roles.

Usage:
    from app.core.permissions import ensure_caregiver
    ensure_caregiver(current_user)
"""

# ---------------------------
# Local Application Imports
# ---------------------------
from app.models.user import User, UserRole  # User ORM model and role enums
from app.core.exceptions import forbidden_exception  # Standard 403 exception


# ---------------------------
# Permission Checks
# ---------------------------
def ensure_caregiver(user: User):
    """
    Ensure that the current user has the 'caregiver' role.
    
    Raises:
        forbidden_exception: If the user is not a caregiver.
    
    Usage:
        ensure_caregiver(current_user)
    """
    if user.role != UserRole.caregiver:
        raise forbidden_exception