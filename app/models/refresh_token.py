"""
models/refresh_token.py

Defines the RefreshToken SQLAlchemy model.
Refresh tokens maintain user sessions across devices and enable secure token refresh.

Relationships:
    - Each RefreshToken belongs to a User.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone  # for timestamping and timezone-aware dates

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship  # for model relationships

# ---------------------------
# Local Application Imports
# ---------------------------
from app.core.database import Base  # SQLAlchemy declarative base


class RefreshToken(Base):
    """
    SQLAlchemy model representing a refresh token.

    Attributes:
        token_id (int): Primary key.
        user_id (int): FK to User table.
        token_hash (str): Hashed token for secure storage.
        device_info (str | None): Optional info about the device.
        ip_address (str | None): Optional IP where token was issued.
        expires_at (datetime): Expiration timestamp.
        revoked (bool): Indicates if token is revoked.
        created_at (datetime): Creation timestamp.
        revoked_at (datetime | None): Revocation timestamp if revoked.
        replaced_by_token_id (int | None): Token ID that replaced this one.
        user (User): Relationship to the associated User.
    """

    __tablename__ = "refresh_tokens"

    token_id = Column(Integer, primary_key=True, index=True)  # primary key
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # FK to users table
    token_hash = Column(String(255), nullable=False)  # store SHA256 hash of token
    device_info = Column(String(100), nullable=True)  # optional device metadata
    ip_address = Column(String(45), nullable=True)  # optional IP address
    expires_at = Column(DateTime(timezone=True), nullable=False)  # token expiration
    revoked = Column(Boolean, default=False)  # token revocation status
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  # creation timestamp
    revoked_at = Column(DateTime(timezone=True), nullable=True)  # timestamp when revoked
    replaced_by_token_id = Column(Integer, ForeignKey("refresh_tokens.token_id"), nullable=True)  # rotation reference

    # Relationship to the User model
    user = relationship("User", back_populates="refresh_tokens")  # link token to its owner