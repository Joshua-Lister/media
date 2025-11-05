"""
Articles API endpoints.
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def list_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List published articles with pagination."""
    return {"message": "List articles endpoint", "page": page, "limit": limit}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_article(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new article."""
    return {"message": "Create article endpoint"}


@router.get("/{article_id}")
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get article by ID."""
    return {"message": f"Get article {article_id}"}


@router.put("/{article_id}")
async def update_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update article."""
    return {"message": f"Update article {article_id}"}


@router.delete("/{article_id}")
async def delete_article(
    article_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Delete article."""
    return {"message": f"Delete article {article_id}"}
