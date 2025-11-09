from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from apps.api.core.database import get_db
from apps.api.core.deps import get_current_user, require_role
from apps.api.schemas.policy import PolicyCreate, PolicyResponse, PolicyValidateRequest
from apps.api.models.user import User
from apps.api.models.policy import Policy
from apps.api.models.project import Project
from apps.api.services.policy import PolicyEngine

router = APIRouter(prefix="/policies", tags=["policies"])


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_data: PolicyCreate,
    current_user: User = Depends(require_role(["ADMIN", "MAINTAINER"])),
    db: AsyncSession = Depends(get_db),
):
    """Create a new policy."""
    # Validate scope
    if policy_data.scope not in ["GLOBAL", "PROJECT"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scope. Must be GLOBAL or PROJECT",
        )

    # If PROJECT scope, verify project exists
    if policy_data.scope == "PROJECT":
        if not policy_data.project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="project_id is required for PROJECT scope",
            )

        project_result = await db.execute(
            select(Project).where(Project.id == policy_data.project_id)
        )
        project = project_result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

    # Validate rule syntax
    syntax_check = PolicyEngine.validate_rule_syntax(policy_data.rule)
    if not syntax_check["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid rule syntax: {syntax_check['message']}",
        )

    policy = Policy(
        name=policy_data.name,
        scope=policy_data.scope,
        type=policy_data.type,
        rule=policy_data.rule,
        project_id=policy_data.project_id,
    )

    db.add(policy)
    await db.commit()
    await db.refresh(policy)

    return policy


@router.get("", response_model=List[PolicyResponse])
async def list_policies(
    project_id: uuid.UUID = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List policies."""
    query = select(Policy)

    if project_id:
        # Get policies for specific project + global policies
        query = query.where(
            (Policy.project_id == project_id) | (Policy.scope == "GLOBAL")
        )

    result = await db.execute(query)
    policies = result.scalars().all()
    return policies


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: uuid.UUID,
    current_user: User = Depends(require_role(["ADMIN", "MAINTAINER"])),
    db: AsyncSession = Depends(get_db),
):
    """Delete a policy."""
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )

    await db.delete(policy)
    await db.commit()

    return None


@router.post("/validate")
async def validate_policy(
    request: PolicyValidateRequest,
    current_user: User = Depends(get_current_user),
):
    """Validate a policy rule against content."""
    # First validate rule syntax
    syntax_check = PolicyEngine.validate_rule_syntax(request.rule)
    if not syntax_check["valid"]:
        return {
            "valid": False,
            "passed": False,
            "messages": [f"Invalid rule syntax: {syntax_check['message']}"],
        }

    # Evaluate rule against content
    result = PolicyEngine.evaluate(request.rule, request.content)

    return {
        "valid": True,
        "passed": result.passed,
        "messages": result.messages,
    }
