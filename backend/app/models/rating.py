"""
Rating model for article reviews.
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Rating(Base):
    """Rating model for article feedback."""

    __tablename__ = "ratings"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    article_id = Column(
        UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # Rating
    rating = Column(
        Integer,
        nullable=False,
        # CheckConstraint will be added via Alembic
    )

    # Feedback
    feedback = Column(Text, nullable=True)

    # Detailed Ratings
    accuracy_rating = Column(Integer, nullable=True)  # 1-5
    sources_rating = Column(Integer, nullable=True)  # 1-5
    writing_quality_rating = Column(Integer, nullable=True)  # 1-5
    originality_rating = Column(Integer, nullable=True)  # 1-5

    # Fraud Prevention
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)

    # Verification
    verified_purchase = Column(
        Integer, default=0, nullable=False
    )  # 0 = no, 1 = yes (for paid content)

    # Helpful Votes
    helpful_count = Column(Integer, default=0, nullable=False)
    not_helpful_count = Column(Integer, default=0, nullable=False)

    # Timestamp
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
    article = relationship("Article", back_populates="ratings")
    user = relationship("User", back_populates="ratings")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range_check"),
    )

    def __repr__(self) -> str:
        return f"<Rating {self.rating} for article {self.article_id}>"
