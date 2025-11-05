"""
Demo mode dependencies that bypass database requirements.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID

from app.core.config import settings
from app.core.security import decode_token
from app.core.demo_db import get_demo_db, DemoUser

# OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_demo_current_user(
    token: str = Depends(oauth2_scheme),
) -> DemoUser:
    """
    Get current authenticated user from JWT token in demo mode.

    Args:
        token: JWT access token

    Returns:
        DemoUser: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    payload = decode_token(token)
    if not payload:
        raise credentials_exception

    # Verify token type
    if payload.get("type") != "access":
        raise credentials_exception

    # Get user ID from token
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    # Get user from demo database
    demo_db = get_demo_db()
    user = demo_db.get_user_by_id(user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def get_demo_current_active_user(
    current_user: DemoUser = Depends(get_demo_current_user),
) -> DemoUser:
    """
    Get current active user in demo mode.

    Args:
        current_user: Current user from token

    Returns:
        DemoUser: Current active user

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


async def get_demo_current_verified_user(
    current_user: DemoUser = Depends(get_demo_current_active_user),
) -> DemoUser:
    """
    Get current verified user in demo mode.

    Args:
        current_user: Current active user

    Returns:
        DemoUser: Current verified user

    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )
    return current_user


async def get_demo_current_writer(
    current_user: DemoUser = Depends(get_demo_current_verified_user),
) -> DemoUser:
    """
    Get current writer user in demo mode.

    Args:
        current_user: Current verified user

    Returns:
        DemoUser: Current writer user

    Raises:
        HTTPException: If user is not a writer
    """
    if not current_user.is_writer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Writer access required",
        )
    return current_user


async def get_demo_current_superuser(
    current_user: DemoUser = Depends(get_demo_current_active_user),
) -> DemoUser:
    """
    Get current superuser in demo mode.

    Args:
        current_user: Current active user

    Returns:
        DemoUser: Current superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required",
        )
    return current_user
