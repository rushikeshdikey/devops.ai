from pydantic import BaseModel
from datetime import datetime
import uuid


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    plan: str
    status: str
    current_period_start: datetime | None
    current_period_end: datetime | None
    cancel_at_period_end: bool

    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    plan: str  # FREE, PREMIUM, ENTERPRISE
    payment_method_id: str | None = None


class CloudAccountCreate(BaseModel):
    name: str
    provider: str  # AWS, GCP, AZURE
    credentials: dict
    region: str | None = None


class CloudAccountResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    provider: str
    region: str | None
    is_active: bool
    last_synced_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class CostRecommendationResponse(BaseModel):
    id: uuid.UUID
    resource_type: str
    resource_id: str
    recommendation_type: str
    title: str
    description: str
    current_cost: float
    estimated_new_cost: float
    monthly_savings: float
    annual_savings: float
    priority: str
    implementation_effort: str
    status: str
    metadata: dict | None

    class Config:
        from_attributes = True


class CostAnalysisResponse(BaseModel):
    id: uuid.UUID
    cloud_account_id: uuid.UUID
    analysis_date: datetime
    total_monthly_cost: float
    potential_savings: float
    savings_percentage: float
    resource_count: int
    cost_breakdown: dict
    recommendations: list[CostRecommendationResponse] = []

    class Config:
        from_attributes = True


class CostAnalysisRequest(BaseModel):
    cloud_account_id: uuid.UUID


class RecommendationActionRequest(BaseModel):
    action: str  # APPLY or DISMISS
