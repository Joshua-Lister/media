"""
Payments API endpoints.
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.post("/subscribe")
async def create_subscription(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new subscription."""
    return {"message": "Create subscription endpoint"}


@router.post("/donate")
async def create_donation(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Make a one-time donation to a writer."""
    return {"message": "Create donation endpoint"}


@router.get("/earnings")
async def get_earnings(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get writer earnings dashboard."""
    return {"message": "Get earnings endpoint"}


@router.post("/webhook")
async def stripe_webhook(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Handle Stripe webhooks."""
    return {"message": "Stripe webhook endpoint"}
