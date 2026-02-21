"""
repositories/user.py

This module defines the UserRepository for performing CRUD operations
on the User model using an asynchronous SQLAlchemy session.

Features:
- Create new users
- Read users by ID, username, email
- Update user information
- Delete users
"""

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy.ext.asyncio import AsyncSession  # async database session
from sqlalchemy import select, update, delete   # query constructs

# ---------------------------
# Local App Imports
# ---------------------------
from app.models import User  # User SQLAlchemy model
from app.schemas.user import UserCreate, UserUpdate  # Pydantic schemas
from app.core.security import get_password_hash  # password hashing utility

# ---------------------------
# User Repository
# ---------------------------
class UserRepository:
    """
    Repository for managing User database operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db  # store async database session

    # -----------------------
    # CREATE
    # -----------------------
    async def create_user(self, user: UserCreate) -> User:
        """
        Create a new user in the database.
        Password is hashed before storing.
        """
        db_user = User(
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            role=user.role,
            sex=user.sex,
            phone_number=user.phone_number,
            password_hash=get_password_hash(user.password),  # hash password before saving
        )
        self.db.add(db_user)       # stage new user
        await self.db.commit()     # persist to DB
        await self.db.refresh(db_user)  # refresh to get generated ID and timestamps
        return db_user

    # -----------------------
    # READ
    # -----------------------
    async def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their unique ID.
        Returns None if not found.
        """
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        return result.scalars().first()

    async def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their unique username.
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their unique email address.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    # -----------------------
    # UPDATE
    # -----------------------
    async def update_user(self, user_id: int, updates: UserUpdate) -> User | None:
        """
        Update user information.
        If password is provided, it is hashed before storing.
        """
        user = await self.get_by_id(user_id)  # fetch user first
        if not user:
            return None  # user not found

        # Apply updates dynamically
        for field, value in updates.dict(exclude_unset=True).items():
            if field == "password":
                setattr(user, "password_hash", get_password_hash(value))  # hash password
            else:
                setattr(user, field, value)  # set other fields

        self.db.add(user)       # stage changes
        await self.db.commit()  # persist updates
        await self.db.refresh(user)  # refresh to get latest data
        return user

    # -----------------------
    # DELETE
    # -----------------------
    async def delete_user(self, user_id: int) -> bool:
        """
        Delete a user by ID.
        Returns True if deletion was successful, False if user was not found.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False  # user does not exist
        await self.db.delete(user)  # delete user
        await self.db.commit()      # commit deletion
        return True