"""
services/dependent_profile_service.py

Service layer for managing DependentProfile operations.

Responsibilities:
- Create, read, update, delete dependent profiles
- Change passwords for dependents
- Ensure only authorized family members can perform actions
"""

# ---------------------------
# Local App Imports
# ---------------------------
from app.repositories.dependent_profile import DependentProfileRepository
from app.repositories.user import UserRepository
from app.schemas.dependent_profile import (
    DependentProfileCreate,
    DependentProfileStore,
    DependentProfileUpdate,
    DependentProfileRead,
    DependentPasswordChange
)
from app.schemas.user import PasswordChange, UserCreate, UserUpdate
from app.models.dependent_profile import DependentProfile
from app.models.user import User
from app.services.user import UserService
from app.core.permissions import ensure_family_member
from app.core.exceptions import (
    dependent_profile_not_found_exception,
    email_already_exists_exception,
    username_already_exists_exception,
)

# ---------------------------
# DependentProfile Service
# ---------------------------
class DependentProfileService:
    """
    Service handling dependent profile operations.

    Permissions:
        - Only family members can create, update, delete, or change passwords for dependents.
    """

    def __init__(
        self,
        dependent_profile_repo: DependentProfileRepository,
        user_repo: UserRepository,
        user_service: UserService
    ):
        self.dependent_profile_repo = dependent_profile_repo
        self.user_repo = user_repo
        self.user_service = user_service

    # ---------------------------
    # CREATE DEPENDENT PROFILE
    # ---------------------------
    async def create_profile(
        self,
        dependent_profile_data: DependentProfileCreate,
        created_by: int,
        current_user: User
    ) -> DependentProfileRead:
        """Create a new dependent profile with an associated user."""
        ensure_family_member(current_user)

        user_data = UserCreate(
            first_name=dependent_profile_data.first_name,
            middle_name=dependent_profile_data.middle_name,
            last_name=dependent_profile_data.last_name,
            username=dependent_profile_data.username,
            email=dependent_profile_data.email,
            role=dependent_profile_data.role,
            sex=dependent_profile_data.sex,
            birthdate=dependent_profile_data.birthdate,
            phone_number=dependent_profile_data.phone_number,
            password=dependent_profile_data.password,
        )

        # Uniqueness checks
        if await self.user_repo.get_by_username(user_data.username):
            raise username_already_exists_exception
        if user_data.email and await self.user_repo.get_by_email(user_data.email):
            raise email_already_exists_exception

        try:
            user = await self.user_repo.create_user(user_data)

            dependent_profile = DependentProfileStore(
                user_id=user.user_id,
                care_notes=dependent_profile_data.care_notes,
                created_by=created_by
            )
            db_profile = await self.dependent_profile_repo.create_dependent_profile(dependent_profile)
            await self.dependent_profile_repo.db.commit()
            return DependentProfileRead.model_validate(db_profile)

        except Exception:
            await self.dependent_profile_repo.db.rollback()
            raise

    # ---------------------------
    # GET PROFILE BY ID
    # ---------------------------
    async def get_profile(self, dependent_id: int, current_user: User) -> DependentProfileRead:
        """Retrieve a dependent profile by its ID."""
        ensure_family_member(current_user)

        profile = await self.dependent_profile_repo.get_by_id(
            dependent_id, eager_load_user=True, creator_id=current_user.user_id
        )
        if not profile:
            raise dependent_profile_not_found_exception
        return DependentProfileRead.model_validate(profile)

    # ---------------------------
    # GET PROFILE BY USER ID
    # ---------------------------
    async def get_profile_by_user(self, user_id: int, current_user: User) -> DependentProfileRead:
        """Retrieve a dependent profile by associated user ID."""
        ensure_family_member(current_user)

        profile = await self.dependent_profile_repo.get_by_user_id(
            user_id, eager_load_user=True, creator_id=current_user.user_id
        )
        if not profile:
            raise dependent_profile_not_found_exception
        return DependentProfileRead.model_validate(profile)

    # ---------------------------
    # LIST ALL DEPENDENTS FOR FAMILY MEMBER
    # ---------------------------
    async def get_dependents_for_user(self, current_user: User) -> list[DependentProfileRead]:
        """Retrieve all dependents created by the current family member."""
        ensure_family_member(current_user)

        profiles = await self.dependent_profile_repo.get_by_creator(
            creator_id=current_user.user_id, eager_load_user=True
        )
        return [DependentProfileRead.model_validate(p) for p in profiles]

    # ---------------------------
    # UPDATE DEPENDENT PROFILE
    # ---------------------------
    async def update_profile(
        self,
        dependent_id: int,
        updates: DependentProfileUpdate,
        current_user: User
    ) -> DependentProfileRead:
        """Update dependent profile and associated user info."""
        ensure_family_member(current_user)

        profile = await self.dependent_profile_repo.get_by_id(
            dependent_id, eager_load_user=True, creator_id=current_user.user_id
        )
        if not profile:
            raise dependent_profile_not_found_exception

        data = updates.model_dump(exclude_unset=True)
        dependent_fields = {k: v for k, v in data.items() if k in DependentProfile.__table__.columns.keys()}
        user_fields = {k: v for k, v in data.items() if k not in dependent_fields}

        # Uniqueness checks
        if 'username' in user_fields and user_fields['username'] != profile.user.username:
            if await self.user_repo.get_by_username(user_fields['username']):
                raise username_already_exists_exception
        if 'email' in user_fields and user_fields['email'] != profile.user.email:
            if await self.user_repo.get_by_email(user_fields['email']):
                raise email_already_exists_exception

        for field, value in dependent_fields.items():
            setattr(profile, field, value)

        if user_fields:
            await self.user_repo.update_user(profile.user.user_id, UserUpdate(**user_fields))

        try:
            await self.dependent_profile_repo.db.commit()
            await self.dependent_profile_repo.db.refresh(profile)
        except Exception:
            await self.dependent_profile_repo.db.rollback()
            raise

        return DependentProfileRead.model_validate(profile)

    # ---------------------------
    # CHANGE PASSWORD
    # ---------------------------
    async def change_password(
        self,
        dependent_id: int,
        payload: DependentPasswordChange,
        current_user: User
    ) -> dict:
        """Change password for a dependent's associated user."""
        ensure_family_member(current_user)

        profile = await self.dependent_profile_repo.get_by_id(
            dependent_id, eager_load_user=True, creator_id=current_user.user_id
        )
        if not profile or not profile.user:
            raise dependent_profile_not_found_exception

        password_payload = PasswordChange(
            current_password=payload.old_password,
            new_password=payload.new_password
        )
        return await self.user_service.change_password(profile.user.user_id, password_payload)

    # ---------------------------
    # DELETE DEPENDENT PROFILE
    # ---------------------------
    async def delete_profile(self, dependent_id: int, current_user: User) -> dict:
        """Delete a dependent profile and its associated user."""
        ensure_family_member(current_user)

        profile = await self.dependent_profile_repo.get_by_id(
            dependent_id, eager_load_user=True, creator_id=current_user.user_id
        )
        if not profile:
            raise dependent_profile_not_found_exception

        await self.dependent_profile_repo.delete_dependent_profile(dependent_id, creator_id=current_user.user_id)
        await self.user_repo.delete_user(profile.user.user_id)

        return {"detail": "Dependent profile and user deleted successfully."}