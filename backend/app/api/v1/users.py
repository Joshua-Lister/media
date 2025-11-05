"""
Users API endpoints.
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get("/profile")
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get current user profile."""
    # TODO: Implement authentication middleware
    return {"message": "User profile endpoint"}


@router.put("/profile")
async def update_user_profile(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update user profile."""
    return {"message": "Update profile endpoint"}


@router.post("/toggle-mode")
async def toggle_user_mode(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Toggle between reader and writer mode."""
    return {"message": "Toggle mode endpoint"}
