"""
core/config.py

This module defines application settings using Pydantic's BaseSettings.

Features:
- Centralizes environment variables and configuration values
- Database connection configuration
- JWT / authentication secrets and expiration times
- Environment configuration (development, production, etc.)
- Computed properties such as DATABASE_URL for SQLAlchemy
"""

from pydantic_settings import BaseSettings  # BaseSettings provides environment variable parsing and type validation
import os

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables (.env file).

    Attributes:
        ENV (str): Current environment ("development", "production", etc.)
        DB_ENGINE (str): Database engine (e.g., "postgresql+asyncpg")
        DB_HOST (str): Database host (IP address or hostname)
        DB_PORT (int): Database port
        DB_NAME (str): Database name
        DB_USER (str): Database username
        DB_PASSWORD (str): Database password
        ACCESS_SECRET_KEY (str): Secret key for signing JWT access tokens
        REFRESH_SECRET_KEY (str): Secret key for signing JWT refresh tokens
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Access token lifetime in minutes
        REFRESH_TOKEN_EXPIRE_DAYS (int): Refresh token lifetime in days
        ALGORITHM (str): JWT signing algorithm (e.g., "HS256")
        API_PREFIX (str): Base prefix for all API routes
        CARE_SPACE_CODE_EXPIRE_HOURS (int): Number of hours before a care space join code expires
        CARE_SPACE_CODE_LENGTH (int): Length of generated care space join codes
    """

    ENV: str = "development"  # Default environment

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
    # CARE SPACE JOIN CODE CONFIGURATION
    # -------------------------
    CARE_SPACE_CODE_EXPIRE_HOURS: int  # Hours before a generated join code expires
    CARE_SPACE_CODE_LENGTH: int        # Length of the join code

    # -------------------------
    # GEMINI AI API KEY
    # -------------------------
    GEMINI_API_KEY: str

    # -------------------------
    # Computed Properties
    # -------------------------

    @property
    def DATABASE_URL(self) -> str:
        """
        Returns the database URL for SQLAlchemy.

        Priority:
        1. Use full DATABASE_URL environment variable (Render / production)
        2. Otherwise, construct from local DB_* variables (development)
        """
        # Try reading DATABASE_URL from environment (used in Render)
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url

        # Fallback for local development using DB_* variables
        return f"{self.DB_ENGINE}://{self.DB_USER}:{self.DB_PASSWORD}" \
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        """
        Pydantic configuration class for Settings.

        - Automatically loads environment variables from a .env file
        - Ensures proper file encoding
        """
        env_file = ".env"                # Path to .env file
        env_file_encoding = "utf-8"      # Encoding for .env file

# -------------------------
# Create a global settings instance
# -------------------------
# Import this instance anywhere in the project to access configuration values
settings = Settings()