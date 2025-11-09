from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from apps.api.core.database import Base


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
    latest_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("config_versions.id"), nullable=True
    )
    tags: Mapped[list] = mapped_column(JSONB, nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="configs")
    versions: Mapped[list["ConfigVersion"]] = relationship(
        "ConfigVersion",
        back_populates="config",
        foreign_keys="ConfigVersion.config_id",
        cascade="all, delete-orphan",
    )
    latest_version: Mapped["ConfigVersion"] = relationship(
        "ConfigVersion", foreign_keys=[latest_version_id], post_update=True
    )


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
