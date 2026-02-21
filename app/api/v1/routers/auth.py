"""
routers/auth.py

This module defines authentication-related FastAPI routes, including:
- User login (access token)
- Refresh token
- Logout (single and all devices)

Dependencies:
- AuthService for authentication operations
- OAuth2PasswordBearer for token retrieval
- get_current_user for user context

All routes are under the `/auth` prefix.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated  # Used for type hinting with FastAPI Depends

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import APIRouter, Depends  # APIRouter to group routes, Depends for dependency injection
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # OAuth2 utilities

# ---------------------------
# Local Application Imports
# ---------------------------
from app.schemas.token import Token, RefreshTokenRequest  # Token response and refresh token request schemas
from app.schemas.user import UserLogin  # Login input schema
from app.services.auth import AuthService  # Service handling authentication logic
from app.dependencies.auth import get_auth_service, get_current_user  # Dependency functions for DI
from app.core.config import settings  # App settings, including API prefix
from app.models.user import User  # User ORM model

# ---------------------------
# Router Configuration
# ---------------------------
api_prefix = settings.API_PREFIX  # Load API prefix from settings

router = APIRouter(
    tags=["auth"],               # Tag used in Swagger docs
)

# OAuth2 scheme for login form/token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{api_prefix}/auth/token")


# ---------------------------
# Routes
# ---------------------------

@router.post(
    "/token",
    response_model=Token,  # Response model to serialize token info
    description="Login with username and password to receive access and refresh tokens."  # Swagger description
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],  # OAuth2 login form input
    auth_service: AuthService = Depends(get_auth_service),      # Inject AuthService
):
    """
    Authenticate user credentials and return access + refresh tokens.
    """
    login_data = UserLogin(username=form_data.username, password=form_data.password)  # Map form to schema
    return await auth_service.login(login_data)  # Call service to perform login


@router.post(
    "/refresh",
    response_model=Token,
    description="Refresh the access token using a valid refresh token."
)
async def refresh_token(
    request: RefreshTokenRequest,  # Input schema containing refresh token
    auth_service: AuthService = Depends(get_auth_service),  # Inject AuthService
):
    """
    Generate a new access token (and optionally a new refresh token) from an existing refresh token.
    """
    return await auth_service.refresh(request.refresh_token)  # Service handles token validation + rotation


@router.post(
    "/logout",
    description="Logout from the current session/device by revoking the provided refresh token."
)
async def logout(
    request: RefreshTokenRequest,  # Input refresh token to revoke
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Revoke a single refresh token to logout from one session/device.
    """
    await auth_service.logout(request.refresh_token)  # Call service to revoke token
    return {"detail": "Successfully logged out."}  # Response for client


@router.post(
    "/logout_all_me",
    description="Logout from all sessions/devices for the current user."
)
async def logout_all_current(
    current_user: User = Depends(get_current_user),  # Get currently authenticated user
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Revoke all refresh tokens associated with the current user.
    """
    await auth_service.logout_all(current_user.user_id)  # Revoke all tokens for the user
    return {"detail": "Successfully logged out from all devices."}  # Response