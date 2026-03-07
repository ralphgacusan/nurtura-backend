"""
services/care_space_join_code_service.py

Service layer for managing CareSpace join codes.

Responsibilities:
- Generate secure alphanumeric join codes
- Validate member permissions before code creation
- Enforce limits on active codes and roles
- Return join code in read-friendly format (hashed for storage)
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
import secrets
import string
from datetime import datetime, timedelta, timezone

# ---------------------------
# Local App Imports
# ---------------------------
from app.models.care_space_join_code import CareSpaceJoinCode
from app.models.user import User
from app.repositories.care_space_join_code import CareSpaceJoinCodeRepository
from app.repositories.care_space_member import CareSpaceMemberRepository
from app.schemas.care_space_join_code import CareSpaceJoinCodeCreate, CareSpaceJoinCodeRead
from app.core.config import settings
from app.core.security import hash_join_code
from app.core.permissions import ensure_editor_or_owner
from app.core.exceptions import (
    care_space_member_not_found_exception,
    too_many_active_join_codes_exception,
    forbidden_exception
)

# ---------------------------
# CareSpace Join Code Service
# ---------------------------
class CareSpaceJoinCodeService:
    """
    Service for managing CareSpace join codes.

    Attributes:
        join_code_repo (CareSpaceJoinCodeRepository): Repository for join code DB operations.
        member_repo (CareSpaceMemberRepository): Repository for care space membership operations.
    """

    def __init__(
        self,
        join_code_repo: CareSpaceJoinCodeRepository,
        member_repo: CareSpaceMemberRepository
    ):
        """Initialize service with required repositories."""
        self.join_code_repo = join_code_repo
        self.member_repo = member_repo

    # ---------------------------
    # HELPER METHOD: CODE GENERATION
    # ---------------------------
    def generate_alphanumeric_code(self, length: int = 8) -> str:
        """
        Generate a secure random alphanumeric string.

        Args:
            length (int): Length of the generated code. Defaults to 8.

        Returns:
            str: Random alphanumeric string.
        """
        alphabet = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    # ---------------------------
    # CREATE JOIN CODE
    # ---------------------------
    async def generate_join_code(
        self, data: CareSpaceJoinCodeCreate, current_user: User
    ) -> CareSpaceJoinCodeRead:
        """
        Generate a new join code for a care space.

        Steps:
        1. Validate that the current user is a member with editor/owner privileges.
        2. Check for role restrictions (cannot generate owner code).
        3. Enforce limit on active join codes.
        4. Generate and hash a new code.
        5. Store the join code in the repository.
        6. Return a read-friendly schema with plain code and expiration.

        Args:
            data (CareSpaceJoinCodeCreate): Input data including care_space_id and role.
            current_user (User): User requesting code creation.

        Raises:
            care_space_member_not_found_exception: If user is not a member.
            forbidden_exception: If trying to generate 'owner' role code.
            too_many_active_join_codes_exception: If active codes exceed allowed limit.

        Returns:
            CareSpaceJoinCodeRead: Newly created join code with expiration info.
        """
        # Validate membership and permissions
        member = await self.member_repo.get_by_user_and_space(
            current_user.user_id,
            data.care_space_id
        )
        if not member:
            raise care_space_member_not_found_exception

        ensure_editor_or_owner(member)

        # Check active codes and role restrictions
        active_codes = await self.join_code_repo.get_active_codes(data.care_space_id)
        if data.role == "owner":
            raise forbidden_exception
        if len(active_codes) >= 5:
            raise too_many_active_join_codes_exception

        # Generate and hash join code
        generated_code = self.generate_alphanumeric_code(settings.CARE_SPACE_CODE_LENGTH)
        hashed_code = hash_join_code(generated_code)

        # Compute expiration datetime
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.CARE_SPACE_CODE_EXPIRE_HOURS)

        # Store the join code in DB
        join_code = CareSpaceJoinCode(
            code=hashed_code,
            care_space_id=data.care_space_id,
            role=data.role,
            expires_at=expires_at,
            is_used=False
        )
        stored_code = await self.join_code_repo.add(join_code)

        # Return read-friendly code (plain text)
        return CareSpaceJoinCodeRead(
            code=generated_code,
            care_space_id=stored_code.care_space_id,
            role=stored_code.role,
            expires_at=stored_code.expires_at
        )