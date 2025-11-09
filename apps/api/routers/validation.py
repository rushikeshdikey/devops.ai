from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import hashlib

from apps.api.core.database import get_db
from apps.api.core.deps import get_current_user
from apps.api.schemas.validation import ValidationRunResponse, DryRunResponse
from apps.api.models.user import User
from apps.api.models.config import Config, ConfigVersion
from apps.api.models.validation import ValidationRun
from apps.api.services.validators import validate_content

router = APIRouter(tags=["validation"])


@router.post("/versions/{version_id}/validate", response_model=ValidationRunResponse)
async def validate_version(
    version_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate a configuration version."""
    # Get version
    result = await db.execute(select(ConfigVersion).where(ConfigVersion.id == version_id))
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    # Get config to determine type
    config_result = await db.execute(select(Config).where(Config.id == version.config_id))
    config = config_result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found",
        )

    # Validate content
    validation_report = validate_content(version.content, config.type)

    # Create validation run
    validation_run = ValidationRun(
        config_version_id=version_id,
        status=validation_report.status,
        report={
            "status": validation_report.status,
            "issues": [issue.model_dump() for issue in validation_report.issues],
        },
    )

    db.add(validation_run)
    await db.commit()
    await db.refresh(validation_run)

    return validation_run


@router.post("/versions/{version_id}/dry-run", response_model=DryRunResponse)
async def dry_run_version(
    version_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Perform a mock dry-run of a configuration version."""
    # Get version
    result = await db.execute(select(ConfigVersion).where(ConfigVersion.id == version_id))
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    # Get config to determine type
    config_result = await db.execute(select(Config).where(Config.id == version.config_id))
    config = config_result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found",
        )

    # Mock dry-run based on checksum (deterministic)
    # In a real system, this would execute terraform plan or kubectl dry-run
    checksum_int = int(version.checksum[:8], 16)
    changed_resources = (checksum_int % 10) + 1  # 1-10 resources

    if config.type == "K8S_YAML":
        summary = f"Would apply Kubernetes resources from {config.title}"
        diff_summary = f"+ {changed_resources} resources would be created/updated"
    elif config.type == "TERRAFORM":
        summary = f"Terraform plan for {config.title}"
        diff_summary = f"Plan: {changed_resources} to add, 0 to change, 0 to destroy"
    else:
        summary = f"Dry-run for {config.title}"
        diff_summary = f"{changed_resources} changes detected"

    return DryRunResponse(
        success=True,
        summary=summary,
        changed_resources=changed_resources,
        diff_summary=diff_summary,
    )
