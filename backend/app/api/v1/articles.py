"""
Articles API endpoints.
"""
from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def list_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List published articles with pagination."""
    if settings.DEMO_MODE:
        from app.core.demo_db import get_demo_db
        demo_db = get_demo_db()

        # Get all published articles
        articles = [a for a in demo_db.articles.values() if a.status == "published"]

        # Sort by published_at descending (newest first)
        articles.sort(key=lambda x: x.published_at, reverse=True)

        # Format articles with author info and ratings
        formatted_articles = []
        for article in articles:
            author = demo_db.users.get(article.author_id)
            if not author:
                continue

            # Calculate average rating
            article_ratings = [r for r in demo_db.ratings.values() if r.article_id == article.id]
            avg_rating = 0.0
            if article_ratings:
                avg_rating = sum(r.rating for r in article_ratings) / len(article_ratings)

            formatted_articles.append({
                "id": str(article.id),
                "title": article.title,
                "slug": article.slug,
                "summary": article.summary,
                "content": article.content,
                "category": article.category,
                "cover_image_url": article.cover_image_url,
                "author": {
                    "id": str(author.id),
                    "username": author.username,
                    "full_name": author.full_name,
                    "avatar_url": author.avatar_url,
                },
                "reading_time_minutes": article.reading_time_minutes,
                "view_count": article.view_count,
                "average_rating": round(avg_rating, 1),
                "rating_count": len(article_ratings),
                "published_at": article.published_at.isoformat(),
                "created_at": article.created_at.isoformat(),
            })

        # Pagination
        start = (page - 1) * limit
        end = start + limit
        paginated = formatted_articles[start:end]

        return paginated

    return {"message": "Database mode not implemented yet"}


@router.get("/{article_id}")
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get article by ID or slug."""
    if settings.DEMO_MODE:
        from app.core.demo_db import get_demo_db
        demo_db = get_demo_db()

        # Try to find by ID first, then by slug
        article = None
        try:
            article_uuid = UUID(article_id)
            article = demo_db.articles.get(article_uuid)
        except ValueError:
            # Not a valid UUID, search by slug
            for a in demo_db.articles.values():
                if a.slug == article_id:
                    article = a
                    break

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        author = demo_db.users.get(article.author_id)
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")

        # Calculate average rating
        article_ratings = [r for r in demo_db.ratings.values() if r.article_id == article.id]
        avg_rating = 0.0
        if article_ratings:
            avg_rating = sum(r.rating for r in article_ratings) / len(article_ratings)

        return {
            "id": str(article.id),
            "title": article.title,
            "slug": article.slug,
            "summary": article.summary,
            "content": article.content,
            "category": article.category,
            "cover_image_url": article.cover_image_url,
            "author": {
                "id": str(author.id),
                "username": author.username,
                "full_name": author.full_name,
                "avatar_url": author.avatar_url,
            },
            "reading_time_minutes": article.reading_time_minutes,
            "view_count": article.view_count,
            "average_rating": round(avg_rating, 1),
            "rating_count": len(article_ratings),
            "published_at": article.published_at.isoformat(),
            "created_at": article.created_at.isoformat(),
        }

    return {"message": "Database mode not implemented yet"}
