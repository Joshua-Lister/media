"""
Article annotation model for fact-checking and commenting on specific parts.
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class ArticleAnnotation(Base):
    """Model for user annotations on article text (fact-checks, comments, corrections)."""

    __tablename__ = "article_annotations"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    article_id = Column(
        UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # Text Selection - stores the highlighted text position
    selection_text = Column(Text, nullable=False)  # The actual highlighted text
    selection_start_offset = Column(Integer, nullable=False)  # Character offset in article
    selection_end_offset = Column(Integer, nullable=False)  # End character offset

    # Context - paragraph or section identifier
    context_identifier = Column(String(255), nullable=True)  # e.g., "paragraph-5", "section-2"

    # Annotation Type
    annotation_type = Column(
        String(30),
        nullable=False,
        default="comment",
        index=True,
    )  # comment, fact_check, correction, question, support

    # Content
    comment = Column(Text, nullable=False)  # User's annotation text

    # For fact-checks: supporting evidence
    evidence_url = Column(Text, nullable=True)  # URL to source
    evidence_title = Column(String(500), nullable=True)  # Title of source
    evidence_excerpt = Column(Text, nullable=True)  # Relevant quote from source

    # Verification Status (for fact-checks)
    is_verified = Column(Boolean, default=False, nullable=False)  # Verified by moderators
    verification_status = Column(
        String(30),
        nullable=True,
        default="pending",
    )  # pending, verified_accurate, verified_inaccurate, disputed

    # Engagement
    upvotes = Column(Integer, default=0, nullable=False)
    downvotes = Column(Integer, default=0, nullable=False)
    reply_count = Column(Integer, default=0, nullable=False)

    # Parent annotation (for threaded discussions)
    parent_annotation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("article_annotations.id"),
        nullable=True,
        index=True,
    )

    # Flags
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)  # Hidden by moderators

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

    # Relationships
    article = relationship("Article", back_populates="annotations")
    user = relationship("User", back_populates="annotations")
    parent = relationship("ArticleAnnotation", remote_side=[id], backref="replies")

    def __repr__(self) -> str:
        return f"<Annotation {self.annotation_type} on article {self.article_id}>"
