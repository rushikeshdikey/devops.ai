from __future__ import annotationsfrom __future__ import annotationsfrom __future__ import annotationsfrom datetime import datetimefrom __future__ import annotations

from datetime import datetime

from typing import TYPE_CHECKINGfrom datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, select

from sqlalchemy.ext.asyncio import AsyncSessionfrom typing import TYPE_CHECKINGfrom datetime import datetime

from sqlalchemy.dialects.postgresql import UUID, JSONB

from sqlalchemy.orm import Mapped, mapped_column, relationshipfrom sqlalchemy import String, DateTime, ForeignKey, Text, Integer, select

import uuid

from apps.api.core.database import Basefrom sqlalchemy.ext.asyncio import AsyncSessionfrom typing import TYPE_CHECKINGfrom sqlalchemy import String, DateTime, ForeignKey, Text, Integerfrom datetime import datetime



if TYPE_CHECKING:from sqlalchemy.dialects.postgresql import UUID, JSONB

    from .user import User

    from .project import Projectfrom sqlalchemy.orm import Mapped, mapped_column, relationshipfrom sqlalchemy import String, DateTime, ForeignKey, Text, Integer

    from .validation import ValidationRun

import uuid



class Config(Base):from apps.api.core.database import Basefrom sqlalchemy.dialects.postgresql import UUID, JSONBfrom sqlalchemy.dialects.postgresql import UUID, JSONBfrom typing import TYPE_CHECKING

    __tablename__ = "configs"



    id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4if TYPE_CHECKING:from sqlalchemy.orm import Mapped, mapped_column, relationship

    )

    project_id: Mapped[uuid.UUID] = mapped_column(    from .user import User

        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False

    )    from .project import Projectimport uuidfrom sqlalchemy.orm import Mapped, mapped_column, relationshipfrom sqlalchemy import String, DateTime, ForeignKey, Text, Integer, event

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    type: Mapped[str] = mapped_column(String(50), nullable=False)  # K8S_YAML, TERRAFORM, GENERIC_YAML    from .validation import ValidationRun

    tags: Mapped[list] = mapped_column(JSONB, nullable=True, default=list)

    created_at: Mapped[datetime] = mapped_column(from apps.api.core.database import Base

        DateTime(timezone=True), default=datetime.utcnow, nullable=False

    )

    latest_version_id: Mapped[uuid.UUID | None] = mapped_column(

        UUID(as_uuid=True), nullable=Trueclass Config(Base):import uuidfrom sqlalchemy.dialects.postgresql import UUID, JSONB

    )

    __tablename__ = "configs"

    # Relationships

    project: Mapped["Project"] = relationship("Project", back_populates="configs")if TYPE_CHECKING:

    versions: Mapped[list["ConfigVersion"]] = relationship(

        "ConfigVersion",    id: Mapped[uuid.UUID] = mapped_column(

        back_populates="config",

        cascade="all, delete-orphan",        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4    from .user import Userfrom apps.api.core.database import Basefrom sqlalchemy.orm import Mapped, mapped_column, relationship

        order_by="desc(ConfigVersion.version_number)",

        lazy="dynamic"    )

    )

    project_id: Mapped[uuid.UUID] = mapped_column(    from .project import Project

    async def update_latest_version_id(self, db: AsyncSession) -> None:

        """Update the latest version ID from the versions relationship."""        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False

        result = await db.execute(

            select(ConfigVersion.id)    )    from .validation import ValidationRunimport uuid

            .where(ConfigVersion.config_id == self.id)

            .order_by(ConfigVersion.version_number.desc())    title: Mapped[str] = mapped_column(String(255), nullable=False)

            .limit(1)

        )    type: Mapped[str] = mapped_column(String(50), nullable=False)  # K8S_YAML, TERRAFORM, GENERIC_YAML

        latest_id = result.scalar_one_or_none()

        self.latest_version_id = latest_id    tags: Mapped[list] = mapped_column(JSONB, nullable=True, default=list)



    created_at: Mapped[datetime] = mapped_column(from apps.api.core.database import Base

class ConfigVersion(Base):

    __tablename__ = "config_versions"        DateTime(timezone=True), default=datetime.utcnow, nullable=False



    id: Mapped[uuid.UUID] = mapped_column(    )class Config(Base):

        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4

    )    latest_version_id: Mapped[uuid.UUID | None] = mapped_column(

    config_id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True), ForeignKey("configs.id"), nullable=False        UUID(as_uuid=True), nullable=True    __tablename__ = "configs"class Config(Base):

    )

    version_number: Mapped[int] = mapped_column(Integer, nullable=False)    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    checksum: Mapped[str] = mapped_column(String(64), nullable=False)

    created_by_id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False    # Relationships

    )

    created_at: Mapped[datetime] = mapped_column(    project: Mapped["Project"] = relationship("Project", back_populates="configs")    id: Mapped[uuid.UUID] = mapped_column(    __tablename__ = "configs"if TYPE_CHECKING:

        DateTime(timezone=True), default=datetime.utcnow, nullable=False

    )    versions: Mapped[list["ConfigVersion"]] = relationship(



    # Relationships        "ConfigVersion",        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4

    config: Mapped["Config"] = relationship("Config", back_populates="versions")

    created_by: Mapped["User"] = relationship("User")        back_populates="config",

    validation_runs: Mapped[list["ValidationRun"]] = relationship(

        "ValidationRun", back_populates="config_version", cascade="all, delete-orphan"        cascade="all, delete-orphan",    )    from .user import User

    )
        order_by="desc(ConfigVersion.version_number)",

        lazy="dynamic"    project_id: Mapped[uuid.UUID] = mapped_column(

    )

        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False    id: Mapped[uuid.UUID] = mapped_column(    from .project import Project

    async def update_latest_version_id(self, db: AsyncSession) -> None:

        """Update the latest version ID from the versions relationship."""    )

        result = await db.execute(

            select(ConfigVersion.id)    title: Mapped[str] = mapped_column(String(255), nullable=False)        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4    from .validation import ValidationRun

            .where(ConfigVersion.config_id == self.id)

            .order_by(ConfigVersion.version_number.desc())    type: Mapped[str] = mapped_column(String(50), nullable=False)  # K8S_YAML, TERRAFORM, GENERIC_YAML

            .limit(1)

        )    tags: Mapped[list] = mapped_column(JSONB, nullable=True, default=list)    )

        latest_id = result.scalar_one_or_none()

        self.latest_version_id = latest_id    created_at: Mapped[datetime] = mapped_column(



        DateTime(timezone=True), default=datetime.utcnow, nullable=False    project_id: Mapped[uuid.UUID] = mapped_column(

class ConfigVersion(Base):

    __tablename__ = "config_versions"    )



    id: Mapped[uuid.UUID] = mapped_column(    latest_version_id: Mapped[uuid.UUID | None] = mapped_column(        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=Falseclass Config(Base):

        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4

    )        UUID(as_uuid=True), nullable=True

    config_id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True), ForeignKey("configs.id"), nullable=False    )    )    __tablename__ = "configs"

    )

    version_number: Mapped[int] = mapped_column(Integer, nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    checksum: Mapped[str] = mapped_column(String(64), nullable=False)    # Relationships    title: Mapped[str] = mapped_column(String(255), nullable=False)

    created_by_id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False    project: Mapped["Project"] = relationship("Project", back_populates="configs")

    )

    created_at: Mapped[datetime] = mapped_column(    versions: Mapped[list["ConfigVersion"]] = relationship(    type: Mapped[str] = mapped_column(String(50), nullable=False)  # K8S_YAML, TERRAFORM, GENERIC_YAML    id: Mapped[uuid.UUID] = mapped_column(

        DateTime(timezone=True), default=datetime.utcnow, nullable=False

    )        "ConfigVersion",



    # Relationships        back_populates="config",    tags: Mapped[list] = mapped_column(JSONB, nullable=True, default=list)        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4

    config: Mapped["Config"] = relationship("Config", back_populates="versions")

    created_by: Mapped["User"] = relationship("User")        cascade="all, delete-orphan",

    validation_runs: Mapped[list["ValidationRun"]] = relationship(

        "ValidationRun", back_populates="config_version", cascade="all, delete-orphan"        order_by="desc(ConfigVersion.version_number)",    created_at: Mapped[datetime] = mapped_column(    )

    )
        lazy="dynamic"

    )        DateTime(timezone=True), default=datetime.utcnow, nullable=False    project_id: Mapped[uuid.UUID] = mapped_column(



    async def update_latest_version_id(self, db: AsyncSession) -> None:    )        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False

        """Update the latest version ID from the versions relationship."""

        result = await db.execute(    latest_version_id: Mapped[uuid.UUID | None] = mapped_column(    )

            select(ConfigVersion.id)

            .where(ConfigVersion.config_id == self.id)        UUID(as_uuid=True), nullable=True    title: Mapped[str] = mapped_column(String(255), nullable=False)

            .order_by(ConfigVersion.version_number.desc())

            .limit(1)    )    type: Mapped[str] = mapped_column(

        )

        latest_id = result.scalar_one_or_none()        String(50), nullable=False

        self.latest_version_id = latest_id

    # Relationships    )  # K8S_YAML, TERRAFORM, GENERIC_YAML



class ConfigVersion(Base):    project: Mapped["Project"] = relationship("Project", back_populates="configs")    tags: Mapped[list] = mapped_column(JSONB, nullable=True, default=list)

    __tablename__ = "config_versions"

    versions: Mapped[list["ConfigVersion"]] = relationship(    created_at: Mapped[datetime] = mapped_column(

    id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4        "ConfigVersion", back_populates="config", cascade="all, delete-orphan"        DateTime(timezone=True), default=datetime.utcnow, nullable=False

    )

    config_id: Mapped[uuid.UUID] = mapped_column(    )    )

        UUID(as_uuid=True), ForeignKey("configs.id"), nullable=False

    )

    version_number: Mapped[int] = mapped_column(Integer, nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)    # Relationships

    checksum: Mapped[str] = mapped_column(String(64), nullable=False)

    created_by_id: Mapped[uuid.UUID] = mapped_column(class ConfigVersion(Base):    project: Mapped["Project"] = relationship("Project", back_populates="configs")

        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False

    )    __tablename__ = "config_versions"    versions: Mapped[list["ConfigVersion"]] = relationship(

    created_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True), default=datetime.utcnow, nullable=False        "ConfigVersion",

    )

    id: Mapped[uuid.UUID] = mapped_column(        back_populates="config",

    # Relationships

    config: Mapped["Config"] = relationship("Config", back_populates="versions")        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4        cascade="all, delete-orphan",

    created_by: Mapped["User"] = relationship("User")

    validation_runs: Mapped[list["ValidationRun"]] = relationship(    )        order_by="desc(ConfigVersion.version_number)",

        "ValidationRun", back_populates="config_version", cascade="all, delete-orphan"

    )    config_id: Mapped[uuid.UUID] = mapped_column(        lazy="dynamic"

        UUID(as_uuid=True), ForeignKey("configs.id"), nullable=False    )

    )

    version_number: Mapped[int] = mapped_column(Integer, nullable=False)    latest_version_id: Mapped[uuid.UUID | None] = mapped_column(

    content: Mapped[str] = mapped_column(Text, nullable=False)        UUID(as_uuid=True), nullable=True

    checksum: Mapped[str] = mapped_column(String(64), nullable=False)    )

    created_by_id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False    async def update_latest_version_id(self, db: AsyncSession) -> None:

    )        """Update the latest version ID from the versions relationship."""

    created_at: Mapped[datetime] = mapped_column(        result = await db.execute(

        DateTime(timezone=True), default=datetime.utcnow, nullable=False            select(ConfigVersion.id)

    )            .where(ConfigVersion.config_id == self.id)

            .order_by(ConfigVersion.version_number.desc())

    # Relationships            .limit(1)

    config: Mapped["Config"] = relationship("Config", back_populates="versions")        )

    created_by: Mapped["User"] = relationship("User")        latest_id = result.scalar_one_or_none()

    validation_runs: Mapped[list["ValidationRun"]] = relationship(        self.latest_version_id = latest_id

        "ValidationRun", back_populates="config_version", cascade="all, delete-orphan"

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
