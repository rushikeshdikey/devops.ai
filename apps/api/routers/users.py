from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from apps.api.core.database import get_db
from apps.api.core.deps import get_current_user, require_role
from apps.api.schemas.user import UserResponse, UserUpdate
from apps.api.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.get("", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_role(["ADMIN"])),
    db: AsyncSession = Depends(get_db),
):
    """List all users (ADMIN only)."""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    update: UserUpdate,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: AsyncSession = Depends(get_db),
):
    """Update user role (ADMIN only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Validate role
    valid_roles = ["ADMIN", "MAINTAINER", "VIEWER"]
    if update.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )

    user.role = update.role
    await db.commit()
    await db.refresh(user)

    return user
