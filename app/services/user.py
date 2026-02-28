# services/user.py

"""
Service layer for managing User operations.
Includes registration, account retrieval, updates, password changes, and deletion.

Features:
- Register new users
- Retrieve user account
- Update user account with uniqueness checks
- Change user password with verification
- Delete user account
"""

# ---------------------------
# Local App Imports
# ---------------------------
from app.repositories.user import UserRepository  # user database CRUD
from app.schemas.user import UserCreate, UserUpdate, PasswordChange  # input schemas
from app.models.user import User  # user ORM model
from app.core.exceptions import (
    user_not_found_exception,  # 404 when user doesn't exist
    email_already_exists_exception,  # 400 for duplicate email
    username_already_exists_exception,  # 400 for duplicate username
    invalid_credentials_exception  # 401 for wrong password
)
from app.core.security import verify_password, get_password_hash  # compare plaintext vs hashed passwords

# ---------------------------
# User Service Class
# ---------------------------
class UserService:
    """
    Service handling user account operations.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo  # inject user repository

    # -----------------------
    # Register / Create User
    # -----------------------
    async def register(self, user_data: UserCreate) -> User:
        """
        Register a new user after validating unique email and username.

        Raises:
            email_already_exists_exception
            username_already_exists_exception

        Returns:
            User: The newly created user instance.
        """
        if await self.user_repo.get_by_email(user_data.email):
            raise email_already_exists_exception

        if await self.user_repo.get_by_username(user_data.username):
            raise username_already_exists_exception

        return await self.user_repo.create_user(user_data)

    # -----------------------
    # Get User Account
    # -----------------------
    async def get_account(self, user_id: int) -> User:
        """
        Retrieve a user's account by ID.

        Raises:
            user_not_found_exception

        Returns:
            User: The requested user.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise user_not_found_exception
        return user

    # -----------------------
    # Update User Account
    # -----------------------
    async def update_account(self, user_id: int, updates: UserUpdate) -> User:
        """
        Update user fields with validation for unique email and username.

        Raises:
            email_already_exists_exception
            username_already_exists_exception
            user_not_found_exception

        Returns:
            User: The updated user.
        """
        if updates.email:
            existing_email_user = await self.user_repo.get_by_email(updates.email)
            if existing_email_user and existing_email_user.user_id != user_id:
                raise email_already_exists_exception

        if updates.username:
            existing_username_user = await self.user_repo.get_by_username(updates.username)
            if existing_username_user and existing_username_user.user_id != user_id:
                raise username_already_exists_exception

        user = await self.user_repo.update_user(user_id, updates)
        if not user:
            raise user_not_found_exception
        return user

    # -----------------------
    # Change User Password
    # -----------------------
    async def change_password(self, user_id: int, payload: PasswordChange) -> dict:
        """
        Change the user's password after verifying the current password.

        Raises:
            user_not_found_exception
            invalid_credentials_exception

        Returns:
            dict: Success message.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise user_not_found_exception

        if not verify_password(payload.current_password, user.password_hash):
            raise invalid_credentials_exception

        hashed_password = get_password_hash(payload.new_password)
        await self.user_repo.change_password(user_id, hashed_password)

        return {"detail": "Password updated successfully."}

    # -----------------------
    # Delete User Account
    # -----------------------
    async def delete_account(self, user_id: int) -> dict:
        """
        Delete a user's account.

        Raises:
            user_not_found_exception

        Returns:
            dict: Success message.
        """
        success = await self.user_repo.delete_user(user_id)
        if not success:
            raise user_not_found_exception

        return {"detail": "Your account has been deleted successfully."}