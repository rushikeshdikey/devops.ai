from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, event
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from apps.api.core.database import Base

if TYPE_CHECKING:
    from .user import User
    from .project import Project
    from .validation import ValidationRun


class Config(Base):
    __tablename__ = "configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # K8S_YAML, TERRAFORM, GENERIC_YAML
    tags: Mapped[list] = mapped_column(JSONB, nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="configs")
    versions: Mapped[list["ConfigVersion"]] = relationship(
        "ConfigVersion",
        back_populates="config",
        cascade="all, delete-orphan",
        order_by="desc(ConfigVersion.version_number)",
        lazy="dynamic"
    )

    latest_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    async def update_latest_version_id(self, db: AsyncSession) -> None:
        """Update the latest version ID from the versions relationship."""
        result = await db.execute(
            select(ConfigVersion.id)
            .where(ConfigVersion.config_id == self.id)
            .order_by(ConfigVersion.version_number.desc())
            .limit(1)
        )
        latest_id = result.scalar_one_or_none()
        self.latest_version_id = latest_id


class ConfigVersion(Base):
    __tablename__ = "config_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("configs.id"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA256
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    config: Mapped["Config"] = relationship(
        "Config", back_populates="versions", foreign_keys=[config_id]
    )
    creator: Mapped["User"] = relationship("User", back_populates="created_versions")
    validation_runs: Mapped[list["ValidationRun"]] = relationship(
        "ValidationRun", back_populates="config_version", cascade="all, delete-orphan"
    )
