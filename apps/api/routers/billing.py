from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from apps.api.core.database import get_db
from apps.api.core.deps import get_current_user
from apps.api.schemas.billing import (
    SubscriptionResponse,
    SubscriptionCreate,
    CloudAccountCreate,
    CloudAccountResponse,
)
from apps.api.models.user import User
from apps.api.models.billing import Subscription, CloudAccount

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's current subscription."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        # Create free subscription for new users
        subscription = Subscription(
            user_id=current_user.id,
            plan="FREE",
            status="ACTIVE",
        )
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

    return subscription


@router.post("/subscription", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or update subscription (upgrade/downgrade)."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    # In production, integrate with Stripe here
    # For now, just update the plan

    if subscription:
        subscription.plan = subscription_data.plan
        subscription.status = "ACTIVE"
    else:
        subscription = Subscription(
            user_id=current_user.id,
            plan=subscription_data.plan,
            status="ACTIVE",
        )
        db.add(subscription)

    await db.commit()
    await db.refresh(subscription)

    return subscription


@router.post("/subscription/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel subscription at end of billing period."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found",
        )

    subscription.cancel_at_period_end = True
    await db.commit()

    return {"message": "Subscription will be canceled at the end of the billing period"}
