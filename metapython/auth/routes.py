"""
Authentication API Routes

Provides endpoints for:
- User registration
- Login (OAuth2 password flow)
- Token refresh
- Email verification
- Password reset
- User profile management

References:
- FastAPI OAuth2: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
"""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from metapython.database import get_session, UserCRUD, User, UserRole
from metapython.auth.jwt_handler import get_jwt_handler
from metapython.auth.dependencies import get_current_user, get_current_verified_user
from metapython.core.config import logger


# ========================================
# Pydantic Schemas
# ========================================

class UserCreate(BaseModel):
    """User registration schema."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    institution: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    institution: Optional[str]
    orcid: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request."""
    refresh_token: str


class PasswordReset(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema."""
    full_name: Optional[str] = None
    institution: Optional[str] = None
    orcid: Optional[str] = None


# ========================================
# Router
# ========================================

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new user.

    Args:
        user_data: User registration data
        session: Database session

    Returns:
        Created user

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    existing_user = UserCRUD.get_user_by_username(session, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    existing_email = UserCRUD.get_user_by_email(session, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    try:
        user = UserCRUD.create_user(
            session,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            institution=user_data.institution
        )

        # TODO: Send verification email
        logger.info(f"User registered: {user.username}")

        return user

    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """
    Login and get access token.

    Args:
        form_data: OAuth2 form (username, password)
        session: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = UserCRUD.authenticate_user(
        session,
        username=form_data.username,
        password=form_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate tokens
    jwt_handler = get_jwt_handler()
    access_token = jwt_handler.create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role.value
    )
    refresh_token = jwt_handler.create_refresh_token(
        user_id=user.id,
        username=user.username
    )

    logger.info(f"User logged in: {user.username}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    session: Session = Depends(get_session)
):
    """
    Refresh access token.

    Args:
        token_data: Refresh token
        session: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    jwt_handler = get_jwt_handler()

    # Verify refresh token
    payload = jwt_handler.verify_refresh_token(token_data.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get user
    user = UserCRUD.get_user_by_id(session, payload["user_id"])
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generate new tokens
    access_token = jwt_handler.create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role.value
    )
    new_refresh_token = jwt_handler.create_refresh_token(
        user_id=user.id,
        username=user.username
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update current user profile.

    Args:
        user_update: Update data
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated user
    """
    updated_user = UserCRUD.update_user(
        session,
        user_id=current_user.id,
        **user_update.dict(exclude_unset=True)
    )

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return updated_user


@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    session: Session = Depends(get_session)
):
    """
    Verify user email.

    Args:
        token: Email verification token
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid
    """
    jwt_handler = get_jwt_handler()

    # Decode token
    payload = jwt_handler.decode_token(token, expected_type="verification")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    # Update user
    user = UserCRUD.update_user(
        session,
        user_id=payload["user_id"],
        is_verified=True
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    logger.info(f"Email verified: {user.username}")

    return {"message": "Email verified successfully"}


@router.post("/password-reset")
async def request_password_reset(
    reset_data: PasswordReset,
    session: Session = Depends(get_session)
):
    """
    Request password reset.

    Args:
        reset_data: Password reset request
        session: Database session

    Returns:
        Success message

    Note:
        Always returns success to prevent email enumeration
    """
    user = UserCRUD.get_user_by_email(session, reset_data.email)

    if user:
        # Generate reset token
        jwt_handler = get_jwt_handler()
        reset_token = jwt_handler.create_password_reset_token(
            user_id=user.id,
            email=user.email
        )

        # TODO: Send reset email
        logger.info(f"Password reset requested: {user.username}")

    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    session: Session = Depends(get_session)
):
    """
    Confirm password reset.

    Args:
        reset_confirm: Reset confirmation with new password
        session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If token is invalid
    """
    jwt_handler = get_jwt_handler()

    # Decode token
    payload = jwt_handler.decode_token(reset_confirm.token, expected_type="password_reset")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Update password
    user = UserCRUD.update_user(
        session,
        user_id=payload["user_id"],
        password=reset_confirm.new_password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    logger.info(f"Password reset: {user.username}")

    return {"message": "Password reset successfully"}


__all__ = ['router']
