"""
User Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID

from app.core.config import settings


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)

    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    expertise_tags: Optional[List[str]] = None
    avatar_url: Optional[str] = None


class UserToggleMode(BaseModel):
    """Toggle user mode schema."""

    is_writer: bool


class UserInDB(UserBase):
    """User in database schema."""

    id: UUID
    is_writer: bool
    writer_verified: bool
    writer_rating: int
    is_verified: bool
    is_active: bool
    is_superuser: bool
    two_factor_enabled: bool
    karma_points: int
    reputation_score: int
    subscription_tier: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Public user profile schema."""

    id: UUID
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    is_writer: bool
    writer_verified: bool
    writer_rating: int
    expertise_tags: Optional[List[str]]
    karma_points: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfile(UserPublic):
    """Full user profile schema (for owner)."""

    email: EmailStr
    is_verified: bool
    two_factor_enabled: bool
    subscription_tier: str
    reputation_score: int

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change schema."""

    current_password: str
    new_password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)


class PasswordReset(BaseModel):
    """Password reset schema."""

    token: str
    new_password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)


class EmailVerification(BaseModel):
    """Email verification schema."""

    token: str


class TwoFactorSetup(BaseModel):
    """Two-factor authentication setup response."""

    secret: str
    qr_code_uri: str


class TwoFactorVerify(BaseModel):
    """Two-factor verification schema."""

    token: str = Field(..., min_length=6, max_length=6)
