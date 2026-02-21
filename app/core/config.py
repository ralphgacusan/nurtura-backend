"""
core/config.py

This module defines application settings using Pydantic's BaseSettings.
It centralizes all environment variables and configuration values,
making it easy to access them across the project in a type-safe way.

Features:
- Database connection configuration
- JWT / authentication secrets and expiration times
- Environment (development/production)
- Computed properties such as DATABASE_URL
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables (.env).

    Attributes:
        ENV: Current environment ("development", "production", etc.)
        DB_ENGINE: Database engine (e.g., "postgresql+asyncpg")
        DB_HOST: Database host (IP or hostname)
        DB_PORT: Database port (integer)
        DB_NAME: Database name
        DB_USER: Database username
        DB_PASSWORD: Database password
        ACCESS_SECRET_KEY: Secret key used to sign JWT access tokens
        REFRESH_SECRET_KEY: Secret key used to sign JWT refresh tokens
        ACCESS_TOKEN_EXPIRE_MINUTES: Lifetime of access tokens (in minutes)
        REFRESH_TOKEN_EXPIRE_DAYS: Lifetime of refresh tokens (in days)
        ALGORITHM: JWT signing algorithm (e.g., "HS256")
        API_PREFIX: Base prefix for API routes
    """

    ENV: str = "development"

    # -------------------------
    # DATABASE CONFIGURATION
    # -------------------------
    DB_ENGINE: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # -------------------------
    # JWT / AUTHENTICATION CONFIGURATION
    # -------------------------
    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ALGORITHM: str

    # -------------------------
    # BASE API PREFIX
    # -------------------------
    API_PREFIX: str

    # -------------------------
    # Computed Properties
    # -------------------------
    @property
    def DATABASE_URL(self) -> str:
        """
        Construct the SQLAlchemy database URL from environment variables.

        Returns:
            str: Database connection string in the format:
                 <DB_ENGINE>://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>

        Example:
            postgresql+asyncpg://user:password@localhost:5432/mydb
        """
        return (
            f"{self.DB_ENGINE}://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        """
        Pydantic configuration class.

        Automatically loads environment variables from a .env file
        and ensures proper encoding.
        """
        env_file = ".env"                # Load environment variables from .env
        env_file_encoding = "utf-8"      # Specify file encoding

# -------------------------
# Create a global settings instance
# -------------------------
# Import this instance anywhere in the project to access settings
settings = Settings()