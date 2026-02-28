"""
services/dependent_profile.py

Service layer for managing DependentProfile operations.
Includes creation, reading, updating, deletion, and password management of dependent profiles.

Features:
- Create dependent profile
- Retrieve profile by ID or user ID
- Retrieve all dependents for a caregiver
- Update dependent profile and user info
- Change dependent's password
- Delete dependent profile and associated user
"""

# ---------------------------
# Local App Imports
# ---------------------------
from app.core.security import get_password_hash, verify_password
from app.repositories.dependent_profile import DependentProfileRepository
from app.schemas.dependent_profile import (
    DependentProfileCreate,
    DependentProfileStore,
    DependentProfileUpdate,
    DependentProfileRead,
    DependentPasswordChange
)
from app.core.exceptions import (
    dependent_profile_not_found_exception,  
    email_already_exists_exception,          
    username_already_exists_exception,       
    forbidden_exception
)
from app.repositories.user import UserRepository
from app.schemas.user import PasswordChange, UserCreate, UserUpdate
from app.models.dependent_profile import DependentProfile
from app.models.user import User, UserRole
from app.services.user import UserService
from app.core.permissions import ensure_caregiver

# ---------------------------
# DependentProfile Service Class
# ---------------------------
class DependentProfileService:
    """
    Service handling dependent profile operations.
    Only caregivers are allowed to create, update, delete, or change passwords.
    """

    def __init__(
        self,
        dependent_profile_repo: DependentProfileRepository,
        user_repo: UserRepository,
        user_service: UserService
    ):
        self.dependent_profile_repo = dependent_profile_repo  # dependent profile repository
        self.user_repo = user_repo  # user repository
        self.user_service = user_service  # user service for password updates

    # -----------------------
    # Create dependent profile
    # -----------------------
    async def create_profile(self, dependent_profile_data: DependentProfileCreate, created_by: int, current_user: User) -> DependentProfileRead:
        """
        Create a new dependent profile along with the associated user.

        Only a caregiver can create dependents.

        Args:
            dependent_profile_data (DependentProfileCreate): Info for dependent and user.
            created_by (int): Caregiver user ID creating the dependent.
            current_user (User): Current authenticated caregiver.

        Returns:
            DependentProfileRead: Created dependent profile with user info.
        """
        ensure_caregiver(current_user)

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

        # Check uniqueness
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

    # -----------------------
    # Get dependent profile by ID
    # -----------------------
    async def get_profile(self, dependent_id: int, current_user: User) -> DependentProfileRead:
        """
        Retrieve a dependent profile by its ID.

        Only a caregiver can fetch dependent profiles they created.

        Args:
            dependent_id (int): ID of the dependent profile.
            current_user (User): Current authenticated caregiver.

        Returns:
            DependentProfileRead: Dependent profile with user info.
        """
        ensure_caregiver(current_user)

        profile = await self.dependent_profile_repo.get_by_id(
            dependent_id,
            eager_load_user=True,
            creator_id=current_user.user_id
        )
        if not profile:
            raise dependent_profile_not_found_exception
        return DependentProfileRead.model_validate(profile)

    # -----------------------
    # Get dependent profile by user ID
    # -----------------------
    async def get_profile_by_user(self, user_id: int, current_user: User) -> DependentProfileRead:
        """
        Retrieve a dependent profile by the associated user's ID.

        Only a caregiver can fetch dependent profiles they created.

        Args:
            user_id (int): User ID linked to the dependent profile.
            current_user (User): Current authenticated caregiver.

        Returns:
            DependentProfileRead: Dependent profile with user info.
        """
        ensure_caregiver(current_user)

        profile = await self.dependent_profile_repo.get_by_user_id(
            user_id,
            eager_load_user=True,
            creator_id=current_user.user_id
        )
        if not profile:
            raise dependent_profile_not_found_exception
        return DependentProfileRead.model_validate(profile)

    # -----------------------
    # Get all dependents for caregiver
    # -----------------------
    async def get_dependents_for_user(self, current_user: User) -> list[DependentProfileRead]:
        """
        Retrieve all dependent profiles created by the current caregiver.

        Args:
            current_user (User): Current authenticated caregiver.

        Returns:
            list[DependentProfileRead]: List of dependent profiles.
        """
        ensure_caregiver(current_user)

        profiles = await self.dependent_profile_repo.get_by_creator(
            creator_id=current_user.user_id,
            eager_load_user=True
        )
        return [DependentProfileRead.model_validate(p) for p in profiles]

    # -----------------------
    # Update dependent profile
    # -----------------------
    async def update_profile(self, dependent_id: int, updates: DependentProfileUpdate, current_user: User) -> DependentProfileRead:
        """
        Update a dependent profile and its associated user info.

        Only a caregiver can update dependent profiles they created.

        Args:
            dependent_id (int): ID of the dependent profile.
            updates (DependentProfileUpdate): Fields to update.
            current_user (User): Current authenticated caregiver.

        Returns:
            DependentProfileRead: Updated dependent profile.
        """
        ensure_caregiver(current_user)

        profile = await self.dependent_profile_repo.get_by_id(
            dependent_id,
            eager_load_user=True,
            creator_id=current_user.user_id
        )
        if not profile:
            raise dependent_profile_not_found_exception

        data = updates.model_dump(exclude_unset=True)
        dependent_fields = {k: v for k, v in data.items() if k in DependentProfile.__table__.columns.keys()}
        user_fields = {k: v for k, v in data.items() if k not in dependent_fields}

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

    # -----------------------
    # Change dependent password
    # -----------------------
    async def change_password(self, dependent_id: int, payload: DependentPasswordChange, current_user: User) -> dict:
        """
        Change password for a dependent's associated user.

        Only a caregiver can perform this action.

        Args:
            dependent_id (int): ID of the dependent profile.
            payload (DependentPasswordChange): Old and new password.
            current_user (User): Current authenticated caregiver.

        Returns:
            dict: Success message.
        """
        ensure_caregiver(current_user)

        profile = await self.dependent_profile_repo.get_by_id(
            dependent_id,
            eager_load_user=True,
            creator_id=current_user.user_id
        )
        if not profile or not profile.user:
            raise dependent_profile_not_found_exception

        user_password_payload = PasswordChange(
            current_password=payload.old_password,
            new_password=payload.new_password
        )
        return await self.user_service.change_password(profile.user.user_id, user_password_payload)

    # -----------------------
    # Delete dependent profile
    # -----------------------
    async def delete_profile(self, dependent_id: int, current_user: User) -> dict:
        """
        Delete a dependent profile and its associated user.

        Only a caregiver can perform this action.

        Args:
            dependent_id (int): ID of the dependent profile.
            current_user (User): Current authenticated caregiver.

        Returns:
            dict: Success message.
        """
        ensure_caregiver(current_user)

        profile = await self.dependent_profile_repo.get_by_id(
            dependent_id,
            eager_load_user=True,
            creator_id=current_user.user_id
        )
        if not profile:
            raise dependent_profile_not_found_exception

        await self.dependent_profile_repo.delete_dependent_profile(dependent_id, creator_id=current_user.user_id)
        await self.user_repo.delete_user(profile.user.user_id)

        return {"detail": "Dependent profile and user deleted successfully."}