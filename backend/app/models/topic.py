"""
Topic models for voting system.
"""
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Topic(Base):
    """Topic model for community voting."""

    __tablename__ = "topics"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    proposed_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=True, index=True)
    tags = Column(Text, nullable=True)  # JSON stored as text

    # Voting
    upvotes = Column(Integer, default=0, nullable=False)
    downvotes = Column(Integer, default=0, nullable=False)
    vote_score = Column(Integer, default=0, nullable=False)  # upvotes - downvotes
    trending_score = Column(Numeric(10, 4), default=0, nullable=False)

    # Status
    status = Column(
        String(20), default="active", nullable=False, index=True
    )  # active, closed, archived
    is_featured = Column(Boolean, default=False, nullable=False)

    # Round Information
    round_week = Column(Integer, nullable=True)  # Week number of the year
    round_month = Column(Integer, nullable=True)  # Month number

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    proposed_by = relationship("User")
    votes = relationship("TopicVote", back_populates="topic", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="topic")

    def __repr__(self) -> str:
        return f"<Topic {self.title}>"


class TopicVote(Base):
    """Topic vote model for tracking user votes."""

    __tablename__ = "topic_votes"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    topic_id = Column(
        UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # Vote
    vote_type = Column(String(10), nullable=False)  # upvote, downvote

    # Timestamp
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    topic = relationship("Topic", back_populates="votes")
    user = relationship("User", back_populates="topic_votes")

    def __repr__(self) -> str:
        return f"<TopicVote {self.vote_type} on {self.topic_id}>"
