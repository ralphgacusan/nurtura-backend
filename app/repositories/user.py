"""
repositories/user.py

Repository for managing User ORM objects.
Provides CRUD operations, password management, and queries by username/email.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserRepository:
    """
    Repository for interacting with User records in the database.

    Args:
        db (AsyncSession): SQLAlchemy asynchronous session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db  # store async session for DB operations

    # ---------------------------
    # CREATE
    # ---------------------------
    async def create_user(self, user: UserCreate) -> User:
        """
        Create a new user in the database with hashed password.

        Args:
            user (UserCreate): Pydantic schema containing new user data.

        Returns:
            User: Newly created user instance with primary key assigned.
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
            password_hash=get_password_hash(user.password),  # hash password before storing
        )
        self.db.add(db_user)
        await self.db.flush()  # flush to assign primary key
        return db_user

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their unique ID.

        Args:
            user_id (int): Primary key of the user.

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
            email (str): Email of the user.

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
        Update user information. Hash the password if it is updated.

        Args:
            user_id (int): ID of the user to update.
            updates (UserUpdate): Pydantic schema with updated fields.

        Returns:
            User | None: Updated user, or None if not found.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None

        for field, value in updates.model_dump(exclude_unset=True).items():
            if field == "password":
                setattr(user, "password_hash", get_password_hash(value))  # hash new password
            else:
                setattr(user, field, value)  # update other fields

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # ---------------------------
    # CHANGE PASSWORD
    # ---------------------------
    async def change_password(self, user_id: int, new_hashed_password: str) -> User:
        """
        Update a user's password with a pre-hashed value.

        Args:
            user_id (int): ID of the user.
            new_hashed_password (str): Already hashed new password.

        Returns:
            User: User instance with updated password hash.
        """
        user = await self.get_by_id(user_id)
        user.password_hash = new_hashed_password  # directly set hashed password
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # ---------------------------
    # DELETE
    # ---------------------------
    async def delete_user(self, user_id: int) -> bool:
        """
        Delete a user by their ID.

        Args:
            user_id (int): ID of the user to delete.

        Returns:
            bool: True if deletion succeeded, False if user not found.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True