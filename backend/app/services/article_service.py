"""
Article service for business logic.
"""
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from uuid import UUID
from slugify import slugify
from datetime import datetime

from app.models.article import Article, ArticleVersion
from app.models.user import User


class ArticleService:
    """Service for article operations."""

    @staticmethod
    async def create_article(
        db: AsyncSession,
        author: User,
        title: str,
        content: str,
        summary: Optional[str] = None,
        topic_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        cover_image_url: Optional[str] = None,
        status: str = "draft",
    ) -> Article:
        """
        Create a new article.

        Args:
            db: Database session
            author: Article author
            title: Article title
            content: Article content
            summary: Optional summary
            topic_id: Optional topic ID
            tags: Optional tags
            category: Optional category
            cover_image_url: Optional cover image
            status: Article status

        Returns:
            Article: Created article
        """
        # Generate slug from title
        slug = slugify(title)

        # Ensure slug is unique
        counter = 1
        original_slug = slug
        while True:
            result = await db.execute(select(Article).where(Article.slug == slug))
            if not result.scalar_one_or_none():
                break
            slug = f"{original_slug}-{counter}"
            counter += 1

        # Calculate reading time (rough estimate: 200 words per minute)
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)

        article = Article(
            author_id=author.id,
            topic_id=topic_id,
            title=title,
            slug=slug,
            content=content,
            summary=summary,
            tags=str(tags) if tags else None,
            category=category,
            cover_image_url=cover_image_url,
            status=status,
            reading_time_minutes=reading_time,
        )

        db.add(article)
        await db.commit()
        await db.refresh(article)
        return article

    @staticmethod
    async def get_article_by_id(db: AsyncSession, article_id: UUID) -> Optional[Article]:
        """Get article by ID."""
        result = await db.execute(
            select(Article).where(Article.id == article_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_article_by_slug(db: AsyncSession, slug: str) -> Optional[Article]:
        """Get article by slug."""
        result = await db.execute(select(Article).where(Article.slug == slug))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_published_articles(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
    ) -> List[Article]:
        """
        Get published articles with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records
            category: Optional category filter

        Returns:
            List[Article]: List of articles
        """
        query = (
            select(Article)
            .where(Article.status == "published")
            .order_by(Article.published_at.desc())
        )

        if category:
            query = query.where(Article.category == category)

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_trending_articles(
        db: AsyncSession, limit: int = 10
    ) -> List[Article]:
        """
        Get trending articles based on recent views and ratings.

        Args:
            db: Database session
            limit: Number of articles to return

        Returns:
            List[Article]: Trending articles
        """
        # Simple trending: recent + high ratings + views
        result = await db.execute(
            select(Article)
            .where(Article.status == "published")
            .order_by(
                Article.view_count.desc(),
                Article.average_rating.desc(),
                Article.published_at.desc(),
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_user_articles(
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> List[Article]:
        """Get articles by user."""
        query = select(Article).where(Article.author_id == user_id)

        if status:
            query = query.where(Article.status == status)

        query = query.order_by(Article.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_article(
        db: AsyncSession, article: Article, update_data: Dict
    ) -> Article:
        """Update article."""
        for field, value in update_data.items():
            if hasattr(article, field) and value is not None:
                setattr(article, field, value)

        await db.commit()
        await db.refresh(article)
        return article

    @staticmethod
    async def publish_article(db: AsyncSession, article: Article) -> Article:
        """Publish an article."""
        article.status = "published"
        article.published_at = datetime.utcnow()
        await db.commit()
        await db.refresh(article)
        return article

    @staticmethod
    async def increment_view_count(db: AsyncSession, article: Article) -> Article:
        """Increment article view count."""
        article.view_count += 1
        await db.commit()
        await db.refresh(article)
        return article

    @staticmethod
    async def delete_article(db: AsyncSession, article: Article) -> None:
        """Delete an article."""
        await db.delete(article)
        await db.commit()

    @staticmethod
    async def search_articles(
        db: AsyncSession, query: str, skip: int = 0, limit: int = 20
    ) -> List[Article]:
        """
        Search articles by title or content.

        Args:
            db: Database session
            query: Search query
            skip: Records to skip
            limit: Maximum records

        Returns:
            List[Article]: Matching articles
        """
        search_term = f"%{query}%"
        result = await db.execute(
            select(Article)
            .where(Article.status == "published")
            .where(
                or_(
                    Article.title.ilike(search_term),
                    Article.summary.ilike(search_term),
                    Article.content.ilike(search_term),
                )
            )
            .order_by(Article.published_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def count_published_articles(db: AsyncSession) -> int:
        """Count published articles."""
        result = await db.execute(
            select(func.count(Article.id)).where(Article.status == "published")
        )
        return result.scalar_one()
