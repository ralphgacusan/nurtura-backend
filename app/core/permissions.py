"""
core/permissions.py

Reusable permission checks for role-based and care-space based access control.

All care-space permissions are derived from `role_in_space` and user roles.
These functions raise `forbidden_exception` when the check fails.

Usage Example:
    from app.core.permissions import ensure_owner
    ensure_owner(care_space_member_instance)
"""

# ---------------------------
# Local Imports
# ---------------------------
from app.models.care_space_member import CareSpaceMember  # CareSpaceMember model
from app.models.user import User, UserRole                 # User model and enum for roles
from app.core.exceptions import forbidden_exception       # Standard 403 exception for forbidden actions

# ---------------------------
# Role-based checks
# ---------------------------
def ensure_family_member(user: User):
    """
    Ensure the user has role 'family_member'.

    Raises:
        forbidden_exception: if the user's role is not 'family_member'
    """
    if user.role != UserRole.family_member:
        raise forbidden_exception


def ensure_caregiver(user: User):
    """
    Ensure the user has role 'caregiver'.

    Raises:
        forbidden_exception: if the user's role is not 'caregiver'
    """
    if user.role != UserRole.caregiver:
        raise forbidden_exception


# ---------------------------
# Care-space membership checks
# ---------------------------
def ensure_member(member: CareSpaceMember):
    """
    Ensure the user is a member of the care space.

    Raises:
        forbidden_exception: if member is None
    """
    if not member:
        raise forbidden_exception


def ensure_owner(member: CareSpaceMember):
    """
    Ensure the user is the owner of the care space.

    Raises:
        forbidden_exception: if member's role_in_space is not 'owner'
    """
    if member.role_in_space != "owner":
        raise forbidden_exception


def ensure_editor_or_owner(member: CareSpaceMember):
    """
    Ensure the user is an editor or owner of the care space.

    Raises:
        forbidden_exception: if member's role_in_space is neither 'owner' nor 'editor'
    """
    if member.role_in_space not in ("owner", "editor"):
        raise forbidden_exception


# ---------------------------
# Combined convenience checks
# ---------------------------
def ensure_family_owner(member: CareSpaceMember, user: User):
    """
    Ensure the user is a family member AND the owner of the care space.

    Raises:
        forbidden_exception: if user is not family_member or not owner
    """
    ensure_family_member(user)
    ensure_owner(member)


def ensure_family_member_and_can_manage_tasks(member: CareSpaceMember, user: User):
    """
    Ensure the user is a family member AND can manage tasks (owner or editor).

    Raises:
        forbidden_exception: if user is not family_member or cannot manage tasks
    """
    ensure_family_member(user)
    ensure_editor_or_owner(member)


def ensure_member_and_can_manage_tasks(member: CareSpaceMember):
    """
    Ensure the member is part of the care space AND can manage tasks.

    Raises:
        forbidden_exception: if member is None or not editor/owner
    """
    ensure_member(member)
    ensure_editor_or_owner(member)


def ensure_family_member_owner_and_manage_tasks(member: CareSpaceMember, user: User):
    """
    Ensure the user is a family member, owner, and can manage tasks.

    Raises:
        forbidden_exception: if any of the conditions fail
    """
    ensure_family_member(user)
    ensure_owner(member)
    ensure_editor_or_owner(member)