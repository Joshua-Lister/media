"""
User service for business logic.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service for user operations."""

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            User: Created user
        """
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

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user(
        db: AsyncSession, user: User, user_data: UserUpdate
    ) -> User:
        """
        Update user information.

        Args:
            db: Database session
            user: User to update
            user_data: Update data

        Returns:
            User: Updated user
        """
        update_dict = user_data.dict(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def toggle_writer_mode(db: AsyncSession, user: User) -> User:
        """
        Toggle user between reader and writer mode.

        Args:
            db: Database session
            user: User to toggle

        Returns:
            User: Updated user
        """
        user.is_writer = not user.is_writer
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def verify_email(db: AsyncSession, user: User) -> User:
        """Verify user email."""
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_writers(
        db: AsyncSession, skip: int = 0, limit: int = 20
    ) -> List[User]:
        """Get list of writers."""
        result = await db.execute(
            select(User)
            .where(User.is_writer == True)
            .where(User.is_active == True)
            .order_by(User.writer_rating.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def count_users(db: AsyncSession) -> int:
        """Count total users."""
        result = await db.execute(select(func.count(User.id)))
        return result.scalar_one()
