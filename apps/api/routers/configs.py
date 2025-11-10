from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
import hashlib

from apps.api.core.database import get_db
from apps.api.core.deps import get_current_user
from apps.api.schemas.config import ConfigCreate, ConfigResponse, ConfigVersionCreate, ConfigVersionResponse
from apps.api.models.user import User
from apps.api.models.project import Project
from apps.api.models.config import Config, ConfigVersion
from apps.api.models.audit import AuditLog

router = APIRouter(tags=["configs"])


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


@router.post("/projects/{project_id}/configs", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    project_id: uuid.UUID,
    config_data: ConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new configuration."""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Validate config type
    valid_types = ["K8S_YAML", "TERRAFORM", "GENERIC_YAML"]
    if config_data.type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid config type. Must be one of: {', '.join(valid_types)}",
        )

    config = Config(
        project_id=project_id,
        title=config_data.title,
        type=config_data.type,
        tags=config_data.tags,
        latest_version_id=None  # New configs have no versions
    )

    db.add(config)
    await db.commit()
    await db.refresh(config)

    # Create audit log
    await create_audit_log(
        db,
        current_user.id,
        "CONFIG_CREATED",
        "Config",
        config.id,
        {"title": config.title, "type": config.type},
    )
    await db.commit()

    return config


@router.get("/projects/{project_id}/configs", response_model=List[ConfigResponse])
async def list_configs(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all configurations for a project."""
    result = await db.execute(select(Config).where(Config.project_id == project_id))
    configs = result.scalars().all()
    
    # Update latest_version_id for each config
    for config in configs:
        await config.update_latest_version_id(db)
    
    return configs


@router.get("/configs/{config_id}", response_model=ConfigResponse)
async def get_config(
    config_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get configuration by ID."""
    result = await db.execute(select(Config).where(Config.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found",
        )

    return config


@router.delete("/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    config_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a configuration."""
    result = await db.execute(select(Config).where(Config.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found",
        )

    # Check permissions
    project_result = await db.execute(select(Project).where(Project.id == config.project_id))
    project = project_result.scalar_one_or_none()

    if project.created_by_id != current_user.id and current_user.role not in ["ADMIN", "MAINTAINER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete this configuration",
        )

    # Create audit log before deleting
    await create_audit_log(
        db,
        current_user.id,
        "CONFIG_DELETED",
        "Config",
        config.id,
        {"title": config.title},
    )

    await db.delete(config)
    await db.commit()

    return None


@router.post("/configs/{config_id}/versions", response_model=ConfigVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    config_id: uuid.UUID,
    version_data: ConfigVersionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new version for a configuration."""
    # Verify config exists
    result = await db.execute(select(Config).where(Config.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found",
        )

    # Get latest version number
    versions_result = await db.execute(
        select(ConfigVersion)
        .where(ConfigVersion.config_id == config_id)
        .order_by(ConfigVersion.version_number.desc())
        .limit(1)
    )
    latest_version = versions_result.scalar_one_or_none()
    next_version_number = (latest_version.version_number + 1) if latest_version else 1

    # Compute checksum
    checksum = hashlib.sha256(version_data.content.encode()).hexdigest()

    # Create new version
    new_version = ConfigVersion(
        config_id=config_id,
        version_number=next_version_number,
        content=version_data.content,
        checksum=checksum,
        created_by_id=current_user.id,
    )

    db.add(new_version)
    await db.flush()  # Get the ID without committing

    # Update config's latest_version_id
    config.latest_version_id = new_version.id
    await db.commit()
    await db.refresh(new_version)

    # Create audit log
    await create_audit_log(
        db,
        current_user.id,
        "VERSION_CREATED",
        "ConfigVersion",
        new_version.id,
        {"config_id": str(config_id), "version_number": next_version_number},
    )
    await db.commit()

    return new_version


@router.get("/configs/{config_id}/versions", response_model=List[ConfigVersionResponse])
async def list_versions(
    config_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all versions for a configuration."""
    result = await db.execute(
        select(ConfigVersion)
        .where(ConfigVersion.config_id == config_id)
        .order_by(ConfigVersion.version_number.desc())
    )
    versions = result.scalars().all()
    return versions


@router.get("/versions/{version_id}", response_model=ConfigVersionResponse)
async def get_version(
    version_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get version by ID."""
    result = await db.execute(select(ConfigVersion).where(ConfigVersion.id == version_id))
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    return version


@router.get("/versions/{version_id}/diff")
async def get_version_diff(
    version_id: uuid.UUID,
    base: str = "prev",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get diff between versions."""
    # Get current version
    result = await db.execute(select(ConfigVersion).where(ConfigVersion.id == version_id))
    current_version = result.scalar_one_or_none()

    if not current_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    # Get base version
    if base == "prev":
        base_version_number = current_version.version_number - 1
        if base_version_number < 1:
            return {
                "unified_diff": "",
                "hunks": [],
                "message": "No previous version to compare",
            }

        base_result = await db.execute(
            select(ConfigVersion)
            .where(
                ConfigVersion.config_id == current_version.config_id,
                ConfigVersion.version_number == base_version_number,
            )
        )
        base_version = base_result.scalar_one_or_none()

        if not base_version:
            return {
                "unified_diff": "",
                "hunks": [],
                "message": "Previous version not found",
            }
    else:
        # Assume base is a version ID
        try:
            base_uuid = uuid.UUID(base)
            base_result = await db.execute(select(ConfigVersion).where(ConfigVersion.id == base_uuid))
            base_version = base_result.scalar_one_or_none()

            if not base_version:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Base version not found",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid base version ID",
            )

    # Generate diff
    import difflib

    base_lines = base_version.content.splitlines(keepends=True)
    current_lines = current_version.content.splitlines(keepends=True)

    unified_diff = "".join(
        difflib.unified_diff(
            base_lines,
            current_lines,
            fromfile=f"version_{base_version.version_number}",
            tofile=f"version_{current_version.version_number}",
        )
    )

    # Generate structured hunks for UI
    hunks = []
    diff_lines = list(difflib.unified_diff(base_lines, current_lines, lineterm=""))

    current_hunk = None
    for line in diff_lines:
        if line.startswith("@@"):
            if current_hunk:
                hunks.append(current_hunk)
            current_hunk = {"header": line, "lines": []}
        elif current_hunk is not None:
            if not line.startswith("---") and not line.startswith("+++"):
                current_hunk["lines"].append(line)

    if current_hunk:
        hunks.append(current_hunk)

    return {
        "unified_diff": unified_diff,
        "hunks": hunks,
        "base_version": base_version.version_number,
        "current_version": current_version.version_number,
    }
