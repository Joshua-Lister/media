"""
Topics API endpoints for voting on journalism topics.
"""
from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.schemas.topic import TopicCreate, TopicResponse, TopicVoteRequest, TopicWithArticleCount

# Import demo mode components
if settings.DEMO_MODE:
    from app.core.demo_db import get_demo_db, DemoTopic
    from app.core.demo_deps import get_demo_current_verified_user as get_current_verified_user
else:
    from app.models.topic import Topic, TopicVote
    from app.models.article import Article
    from app.core.deps import get_current_verified_user

router = APIRouter()


@router.get("/", response_model=List[TopicWithArticleCount])
async def list_topics(
    skip: int = 0,
    limit: int = 20,
    category: str = None,
    tags: str = None,  # Comma-separated tags
    search: str = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    List all active topics sorted by trending score.

    **Filters:**
    - category: Filter by category (e.g., "Environment", "Politics", "Health")
    - tags: Filter by tags (comma-separated, e.g., "climate,energy")
    - search: Search in title and description

    **Demo Mode**: Returns pre-seeded topics from demo database.
    """
    if settings.DEMO_MODE:
        demo_db = get_demo_db()

        # Parse tags if provided
        tag_list = [t.strip() for t in tags.split(",")] if tags else None

        topics = demo_db.get_topics(
            skip=skip,
            limit=limit,
            category=category,
            tags=tag_list,
            search=search
        )

        # Convert to response format
        result = []
        for topic in topics:
            result.append({
                "id": str(topic.id),
                "title": topic.title,
                "description": topic.description,
                "category": topic.category,
                "tags": topic.tags,
                "created_by": str(topic.id),
                "upvotes": topic.vote_count,
                "downvotes": 0,
                "trending_score": float(topic.vote_count),
                "is_featured": False,
                "created_at": topic.created_at.isoformat(),
                "net_votes": topic.vote_count,
                "article_count": 0,
                "user_vote": None,
            })
        return result

    # Database mode - implementation continues...
    return []


@router.get("/recommended", response_model=List[TopicWithArticleCount])
async def get_recommended_topics(
    limit: int = 10,
    current_user = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get personalized topic recommendations based on user interests.

    Learns from:
    - Topics the user has voted on
    - Articles the user has read
    - Categories and tags the user engages with

    **Demo Mode**: Returns topics based on tracked user interests.
    """
    if settings.DEMO_MODE:
        demo_db = get_demo_db()
        recommended_topics = demo_db.get_recommended_topics(
            user_id=current_user.id,
            limit=limit
        )

        # Convert to response format
        result = []
        for topic in recommended_topics:
            result.append({
                "id": str(topic.id),
                "title": topic.title,
                "description": topic.description,
                "category": topic.category,
                "tags": topic.tags,
                "created_by": str(topic.id),
                "upvotes": topic.vote_count,
                "downvotes": 0,
                "trending_score": float(topic.vote_count),
                "is_featured": False,
                "created_at": topic.created_at.isoformat(),
                "net_votes": topic.vote_count,
                "article_count": 0,
                "user_vote": None,
            })
        return result

    return []


@router.post("/{topic_id}/vote", response_model=TopicResponse)
async def vote_on_topic(
    topic_id: UUID,
    vote_data: TopicVoteRequest,
    current_user = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Vote on a topic (upvote/downvote)."""
    if settings.DEMO_MODE:
        demo_db = get_demo_db()
        topic = demo_db.get_topic_by_id(topic_id)

        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        # Update vote
        if vote_data.vote_type == "upvote":
            topic.vote_count += 1
        else:
            topic.vote_count = max(0, topic.vote_count - 1)

        # Track user interest
        demo_db.track_user_interest(
            user_id=current_user.id,
            category=topic.category,
            tags=topic.tags,
            topic_id=topic.id
        )

        return {
            "id": str(topic.id),
            "title": topic.title,
            "description": topic.description,
            "created_by": str(topic.id),
            "upvotes": topic.vote_count,
            "downvotes": 0,
            "trending_score": float(topic.vote_count),
            "is_featured": False,
            "created_at": topic.created_at.isoformat(),
            "net_votes": topic.vote_count,
            "user_vote": vote_data.vote_type,
        }
    return {}
