"""
models/refresh_token.py

This module defines the RefreshToken ORM model for SQLAlchemy.
Refresh tokens are used to maintain user sessions across devices
and allow secure generation of new access tokens.

Fields:
- token_id: Primary key for the refresh token
- user_id: Foreign key linking to the owning user
- token_hash: Secure hash of the refresh token
- device_info: Optional metadata about the device
- ip_address: Optional IP address where token was issued
- expires_at: Expiration datetime for the token
- revoked: Boolean flag indicating if the token is revoked
- created_at: Timestamp when the token was created
- revoked_at: Timestamp when the token was revoked (if applicable)
- replaced_by_token_id: Reference to another RefreshToken that replaced this one (token rotation)

Relationships:
- user: Many-to-one relationship with the owning User
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone  # for timezone-aware timestamps

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

# ---------------------------
# Local App Imports
# ---------------------------
from app.core.database import Base  # Declarative base for ORM models

# ---------------------------
# RefreshToken Model
# ---------------------------
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    # Primary key
    token_id = Column(Integer, primary_key=True, index=True)

    # FK to the owning user
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # Secure hash of the refresh token
    token_hash = Column(String(255), nullable=False)

    # Optional device information (e.g., browser, device type)
    device_info = Column(String(100), nullable=True)

    # Optional IP address where token was issued
    ip_address = Column(String(45), nullable=True)

    # Expiration datetime of the token
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Revocation status
    revoked = Column(Boolean, default=False)

    # Creation timestamp (UTC)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Revocation timestamp (if revoked)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Reference to the token that replaced this one (token rotation)
    replaced_by_token_id = Column(Integer, ForeignKey("refresh_tokens.token_id"), nullable=True)

    # ---------------------------
    # Relationships
    # ---------------------------

    # Owner of this refresh token
    user = relationship("User", back_populates="refresh_tokens")