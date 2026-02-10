"""
User model.
"""
from datetime import datetime
from typing import List
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class User(Base):
    """User model with dual mode (reader/writer) support."""

    __tablename__ = "users"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    expertise_tags = Column(Text, nullable=True)  # JSON stored as text

    # User Mode
    is_writer = Column(Boolean, default=False, nullable=False)
    writer_verified = Column(Boolean, default=False, nullable=False)
    writer_rating = Column(Integer, default=0)  # Aggregate rating * 100

    # Security
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Two-Factor Authentication
    two_factor_secret = Column(String(32), nullable=True)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)

    # Account Security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(INET, nullable=True)

    # Password History (for preventing reuse)
    password_history = Column(Text, nullable=True)  # JSON stored as text

    # Email Verification
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Password Reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    # Reputation & Karma
    karma_points = Column(Integer, default=0, nullable=False)
    reputation_score = Column(Integer, default=0, nullable=False)

    # Subscription
    subscription_tier = Column(
        String(20), default="free", nullable=False
    )  # free, premium_reader, premium_writer

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")
    topic_votes = relationship("TopicVote", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    annotations = relationship("ArticleAnnotation", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship(
        "Subscription",
        foreign_keys="Subscription.subscriber_id",
        back_populates="subscriber",
        cascade="all, delete-orphan",
    )
    followers = relationship(
        "Follower",
        foreign_keys="Follower.following_id",
        back_populates="following",
        cascade="all, delete-orphan",
    )
    following = relationship(
        "Follower",
        foreign_keys="Follower.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
