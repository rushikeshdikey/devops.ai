from datetime import datetimefrom datetime import datetimefrom datetime import datetimefrom datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey

from sqlalchemy.dialects.postgresql import UUID, JSONBfrom sqlalchemy import String, DateTime, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

import uuidfrom sqlalchemy.dialects.postgresql import UUID, JSONBfrom sqlalchemy import String, DateTime, ForeignKeyfrom sqlalchemy import String, DateTime, ForeignKey

from apps.api.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship



class AuditLog(Base):import uuidfrom sqlalchemy.dialects.postgresql import UUID, JSONBfrom sqlalchemy.dialects.postgresql import UUID, JSONB

    __tablename__ = "audit_logs"

from apps.api.core.database import Base

    id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4from sqlalchemy.orm import Mapped, mapped_column, relationshipfrom sqlalchemy.orm import Mapped, mapped_column, relationship

    )

    actor_id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False

    )class AuditLog(Base):import uuidimport uuid

    action: Mapped[str] = mapped_column(String(100), nullable=False)

    subject_type: Mapped[str] = mapped_column(String(100), nullable=False)    __tablename__ = "audit_logs"

    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    audit_metadata: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)from apps.api.core.database import Basefrom apps.api.core.database import Base

    created_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True), default=datetime.utcnow, nullable=False    id: Mapped[uuid.UUID] = mapped_column(

    )

        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4

    # Relationships

    actor: Mapped["User"] = relationship("User")    )

    actor_id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False

    )class AuditLog(Base):class AuditLog(Base):

    action: Mapped[str] = mapped_column(String(100), nullable=False)

    subject_type: Mapped[str] = mapped_column(String(100), nullable=False)    __tablename__ = "audit_logs"    __tablename__ = "audit_logs"

    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    audit_metadata: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)

    created_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True), default=datetime.utcnow, nullable=False    id: Mapped[uuid.UUID] = mapped_column(    id: Mapped[uuid.UUID] = mapped_column(

    )

        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4

    # Relationships

    actor: Mapped["User"] = relationship("User")    )    )

    actor_id: Mapped[uuid.UUID] = mapped_column(    actor_id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False

    )    )

    action: Mapped[str] = mapped_column(String(100), nullable=False)    action: Mapped[str] = mapped_column(String(255), nullable=False)

    subject_type: Mapped[str] = mapped_column(String(100), nullable=False)    subject_type: Mapped[str] = mapped_column(String(255), nullable=False)

    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)    subject_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    audit_metadata: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)    audit_metadata: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)

    created_at: Mapped[datetime] = mapped_column(    created_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True), default=datetime.utcnow, nullable=False        DateTime(timezone=True), default=datetime.utcnow, nullable=False

    )    )



    # Relationships    # Relationships

    actor: Mapped["User"] = relationship("User")    actor: Mapped["User"] = relationship("User", back_populates="audit_logs")
