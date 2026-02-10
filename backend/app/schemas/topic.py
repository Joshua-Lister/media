"""
Topic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class TopicBase(BaseModel):
    """Base topic schema."""
    title: str = Field(..., min_length=5, max_length=200, description="Topic title")
    description: str = Field(..., min_length=20, max_length=1000, description="Topic description")
    category: Optional[str] = Field(default="General", description="Topic category")
    tags: List[str] = Field(default_factory=list, description="Topic tags")


class TopicCreate(TopicBase):
    """Schema for creating a new topic."""
    pass


class TopicVoteRequest(BaseModel):
    """Schema for voting on a topic."""
    vote_type: str = Field(..., pattern="^(upvote|downvote)$", description="Type of vote: upvote or downvote")


class TopicResponse(TopicBase):
    """Schema for topic response."""
    id: UUID
    created_by: UUID
    upvotes: int
    downvotes: int
    trending_score: float
    is_featured: bool
    created_at: datetime

    # Computed fields
    net_votes: int = Field(default=0, description="Net votes (upvotes - downvotes)")
    user_vote: Optional[str] = Field(default=None, description="Current user's vote if any")

    class Config:
        from_attributes = True


class TopicWithArticleCount(TopicResponse):
    """Topic response with article count."""
    article_count: int = Field(default=0, description="Number of articles for this topic")
