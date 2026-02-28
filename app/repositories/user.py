"""
repositories/user.py

This module defines the UserRepository for performing CRUD operations
on the User model using an asynchronous SQLAlchemy session.

Responsibilities:
- Create new users
- Retrieve users by ID, username, or email
- Update user information
- Change user password
- Delete users
"""

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy.ext.asyncio import AsyncSession  # async DB session
from sqlalchemy import select  # query construct

# ---------------------------
# Local App Imports
# ---------------------------
from app.models import User
from app.schemas.user import PasswordChange, UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import user_not_found_exception, invalid_credentials_exception

# ---------------------------
# User Repository
# ---------------------------
class UserRepository:
    """
    Repository for managing User database operations.

    Attributes:
        db (AsyncSession): Asynchronous SQLAlchemy session.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.

        Args:
            db (AsyncSession): Async database session.
        """
        self.db = db

    # ---------------------------
    # CREATE
    # ---------------------------
    async def create_user(self, user: UserCreate) -> User:
        """
        Create a new user in the database.

        The password is hashed before storage.

        Args:
            user (UserCreate): Pydantic schema containing new user data.

        Returns:
            User: Newly created user instance.
        """
        db_user = User(
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            role=user.role,
            sex=user.sex,
            birthdate=user.birthdate,
            phone_number=user.phone_number,
            password_hash=get_password_hash(user.password),
        )
        self.db.add(db_user)
        await self.db.flush()
        return db_user

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their unique ID.

        Args:
            user_id (int): ID of the user.

        Returns:
            User | None: User instance if found, else None.
        """
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        return result.scalars().first()

    async def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their unique username.

        Args:
            username (str): Username of the user.

        Returns:
            User | None: User instance if found, else None.
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their unique email address.

        Args:
            email (str): Email address of the user.

        Returns:
            User | None: User instance if found, else None.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    # ---------------------------
    # UPDATE
    # ---------------------------
    async def update_user(self, user_id: int, updates: UserUpdate) -> User | None:
        """
        Update user information.

        If a password is provided, it is hashed before storage.

        Args:
            user_id (int): ID of the user to update.
            updates (UserUpdate): Pydantic schema with updated fields.

        Returns:
            User | None: Updated user instance, or None if user not found.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None

        for field, value in updates.model_dump(exclude_unset=True).items():
            if field == "password":
                setattr(user, "password_hash", get_password_hash(value))
            else:
                setattr(user, field, value)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # ---------------------------
    # CHANGE PASSWORD
    # ---------------------------
    async def change_password(self, user_id: int, payload: PasswordChange) -> dict:
        """
        Verify the current password and update to a new password.

        Args:
            user_id (int): ID of the user.
            payload (PasswordChange): Contains current and new passwords.

        Raises:
            user_not_found_exception: If user does not exist.
            invalid_credentials_exception: If current password does not match.

        Returns:
            dict: Success message upon password change.
        """
        user = await self.get_by_id(user_id)
        if not user:
            raise user_not_found_exception

        if not verify_password(payload.current_password, user.password_hash):
            raise invalid_credentials_exception

        user.password_hash = get_password_hash(payload.new_password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return {"detail": "Password updated successfully."}

    # ---------------------------
    # DELETE
    # ---------------------------
    async def delete_user(self, user_id: int) -> bool:
        """
        Delete a user by their ID.

        Args:
            user_id (int): ID of the user to delete.

        Returns:
            bool: True if deletion was successful, False if user not found.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True