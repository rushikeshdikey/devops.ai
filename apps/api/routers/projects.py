from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from apps.api.core.database import get_db
from apps.api.core.deps import get_current_user
from apps.api.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from apps.api.models.user import User
from apps.api.models.project import Project
from apps.api.models.audit import AuditLog

router = APIRouter(prefix="/projects", tags=["projects"])


async def create_audit_log(
    db: AsyncSession,
    actor_id: uuid.UUID,
    action: str,
    subject_type: str,
    subject_id: uuid.UUID,
    metadata: dict = None,
):
    """Helper to create audit log entry."""
    audit_log = AuditLog(
        actor_id=actor_id,
        action=action,
        subject_type=subject_type,
        subject_id=subject_id,
        metadata=metadata or {},
    )
    db.add(audit_log)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project."""
    project = Project(
        name=project_data.name,
        description=project_data.description,
        created_by_id=current_user.id,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    # Create audit log
    await create_audit_log(
        db,
        current_user.id,
        "PROJECT_CREATED",
        "Project",
        project.id,
        {"name": project.name},
    )
    await db.commit()

    return project


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all projects."""
    result = await db.execute(select(Project))
    projects = result.scalars().all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get project by ID."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    update_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a project."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check permissions (owner or admin)
    if project.created_by_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update this project",
        )

    # Update fields
    if update_data.name is not None:
        project.name = update_data.name
    if update_data.description is not None:
        project.description = update_data.description

    await db.commit()
    await db.refresh(project)

    # Create audit log
    await create_audit_log(
        db,
        current_user.id,
        "PROJECT_UPDATED",
        "Project",
        project.id,
        {"name": project.name},
    )
    await db.commit()

    return project
