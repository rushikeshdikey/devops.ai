from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Float, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from apps.api.core.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    stripe_customer_id: Mapped[str] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String(255), nullable=True)
    plan: Mapped[str] = mapped_column(String(50), nullable=False)  # FREE, PREMIUM, ENTERPRISE
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # ACTIVE, CANCELED, PAST_DUE
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscription")


class CloudAccount(Base):
    __tablename__ = "cloud_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # AWS, GCP, AZURE
    credentials: Mapped[dict] = mapped_column(JSONB, nullable=False)  # Encrypted credentials
    region: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cloud_accounts")
    cost_analyses: Mapped[list["CostAnalysis"]] = relationship(
        "CostAnalysis", back_populates="cloud_account", cascade="all, delete-orphan"
    )


class CostAnalysis(Base):
    __tablename__ = "cost_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    cloud_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cloud_accounts.id"), nullable=False
    )
    analysis_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_monthly_cost: Mapped[float] = mapped_column(Float, nullable=False)
    potential_savings: Mapped[float] = mapped_column(Float, nullable=False)
    savings_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    resource_count: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_breakdown: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    cloud_account: Mapped["CloudAccount"] = relationship(
        "CloudAccount", back_populates="cost_analyses"
    )
    recommendations: Mapped[list["CostRecommendation"]] = relationship(
        "CostRecommendation", back_populates="cost_analysis", cascade="all, delete-orphan"
    )


class CostRecommendation(Base):
    __tablename__ = "cost_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    cost_analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cost_analyses.id"), nullable=False
    )
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # Types: DOWNSIZE, TERMINATE, RESERVED_INSTANCE, SPOT_INSTANCE, STORAGE_CLASS_CHANGE
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    current_cost: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_new_cost: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_savings: Mapped[float] = mapped_column(Float, nullable=False)
    annual_savings: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)  # HIGH, MEDIUM, LOW
    implementation_effort: Mapped[str] = mapped_column(String(20), nullable=False)  # EASY, MEDIUM, HARD
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, APPLIED, DISMISSED
    recommendation_metadata: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    cost_analysis: Mapped["CostAnalysis"] = relationship(
        "CostAnalysis", back_populates="recommendations"
    )
