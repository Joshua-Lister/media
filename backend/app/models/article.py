"""
Article models.
"""
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Article(Base):
    """Article model for citizen journalism content."""

    __tablename__ = "articles"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True, index=True)

    # Content
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    cover_image_url = Column(String(500), nullable=True)

    # Metadata
    tags = Column(Text, nullable=True)  # JSON stored as text
    category = Column(String(50), nullable=True, index=True)
    reading_time_minutes = Column(Integer, nullable=True)

    # SEO
    meta_description = Column(String(160), nullable=True)
    meta_keywords = Column(Text, nullable=True)

    # Status
    status = Column(
        String(20), default="draft", nullable=False, index=True
    )  # draft, review, published, archived

    # Versioning
    version = Column(Integer, default=1, nullable=False)
    parent_version_id = Column(
        UUID(as_uuid=True), ForeignKey("articles.id"), nullable=True
    )

    # Engagement Metrics
    view_count = Column(Integer, default=0, nullable=False)
    unique_view_count = Column(Integer, default=0, nullable=False)
    average_time_on_page = Column(Integer, default=0, nullable=True)  # in seconds
    scroll_depth_avg = Column(Integer, default=0, nullable=True)  # percentage

    # Ratings
    average_rating = Column(Numeric(3, 2), nullable=True)
    rating_count = Column(Integer, default=0, nullable=False)
    credibility_score = Column(Numeric(3, 2), nullable=True)

    # Editorial
    featured = Column(Boolean, default=False, nullable=False)
    flagged = Column(Boolean, default=False, nullable=False)
    flag_reason = Column(Text, nullable=True)

    # AI Generated
    ai_generated = Column(Boolean, default=False, nullable=False)
    ai_model = Column(String(50), nullable=True)

    # Scheduling
    scheduled_publish_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
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
    author = relationship("User", back_populates="articles")
    topic = relationship("Topic", back_populates="articles")
    ratings = relationship("Rating", back_populates="article", cascade="all, delete-orphan")
    annotations = relationship("ArticleAnnotation", back_populates="article", cascade="all, delete-orphan")
    versions = relationship(
        "Article",
        backref="parent_version",
        remote_side=[id],
        cascade="all, delete-orphan",
    )
    article_versions = relationship(
        "ArticleVersion", back_populates="article", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Article {self.title}>"


class ArticleVersion(Base):
    """Article version history for tracking changes."""

    __tablename__ = "article_versions"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    article_id = Column(
        UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False, index=True
    )

    # Version Info
    version_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    # Change Information
    change_description = Column(Text, nullable=True)
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Timestamp
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    article = relationship("Article", back_populates="article_versions")
    changed_by = relationship("User")

    def __repr__(self) -> str:
        return f"<ArticleVersion {self.version_number} of {self.article_id}>"
