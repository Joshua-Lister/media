"""
Authentication API endpoints.
"""
from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    decode_token,
    verify_totp_token,
)
from app.core.config import settings
from app.schemas.auth import Token, LoginRequest, RefreshTokenRequest
from app.schemas.user import UserCreate, UserInDB

# Import demo mode components
if settings.DEMO_MODE:
    from app.core.demo_db import get_demo_db
else:
    from app.models.user import User
    from sqlalchemy import select

router = APIRouter()


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user

    Raises:
        HTTPException: If email or username already exists
    """
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    User login endpoint.

    **DEMO MODE**: Use email='reader@demo.com' or 'writer@demo.com' with password='password'

    Args:
        login_data: Login credentials
        db: Database session (not used in demo mode)

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    if settings.DEMO_MODE:
        # Demo mode login
        demo_db = get_demo_db()
        user = demo_db.get_user_by_email(login_data.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password. Try: reader@demo.com or writer@demo.com with password 'password'",
            )

        # In demo mode, accept any password for simplicity (or check for "password")
        if login_data.password != "password":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password. Use 'password' for demo accounts",
            )

        # Create tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    # Normal database mode login
    from app.models.user import User
    from sqlalchemy import select

    # Get user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        # Increment failed login attempts
        user.failed_login_attempts += 1
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if account is locked
    if hasattr(user, 'locked_until') and user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked",
        )

    # Check 2FA if enabled
    if hasattr(user, 'two_factor_enabled') and user.two_factor_enabled:
        if not login_data.totp_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA token required",
            )

        if not verify_totp_token(user.two_factor_secret, login_data.totp_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA token",
            )

    # Reset failed login attempts
    if hasattr(user, 'failed_login_attempts'):
        user.failed_login_attempts = 0
    if hasattr(user, 'last_login'):
        user.last_login = datetime.utcnow()
    await db.commit()

    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Refresh access token.

    Args:
        refresh_data: Refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Decode refresh token
    payload = decode_token(refresh_data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Verify user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


# Add missing import
from datetime import datetime
