from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid

from apps.api.core.database import get_db
from apps.api.core.deps import get_current_user, require_role
from apps.api.schemas.audit import AuditLogResponse
from apps.api.models.user import User
from apps.api.models.audit import AuditLog

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    project_id: Optional[uuid.UUID] = None,
    actor_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(require_role(["ADMIN", "MAINTAINER"])),
    db: AsyncSession = Depends(get_db),
):
    """List audit logs with optional filters."""
    query = select(AuditLog).order_by(AuditLog.created_at.desc())

    # Apply filters
    if actor_id:
        query = query.where(AuditLog.actor_id == actor_id)

    if action:
        query = query.where(AuditLog.action == action)

    # Note: project_id filter would require checking subject_id for Project type
    # This is a simplified implementation

    query = query.limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    return logs
