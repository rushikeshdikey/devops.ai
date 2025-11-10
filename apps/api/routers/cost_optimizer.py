from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from datetime import datetime

from apps.api.core.database import get_db
from apps.api.core.deps import get_current_user
from apps.api.schemas.billing import (
    CloudAccountCreate,
    CloudAccountResponse,
    CostAnalysisResponse,
    CostAnalysisRequest,
    CostRecommendationResponse,
    RecommendationActionRequest,
)
from apps.api.models.user import User
from apps.api.models.billing import CloudAccount, CostAnalysis, CostRecommendation, Subscription
from apps.api.services.cost_optimizer import CostOptimizerEngine
from apps.api.services.cost_optimizer.cloud_providers import get_analyzer

router = APIRouter(prefix="/cost-optimizer", tags=["cost-optimizer"])


async def check_subscription_limit(user_id: uuid.UUID, db: AsyncSession):
    """Check if user has reached account limit based on subscription."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    subscription = result.scalar_one_or_none()

    account_result = await db.execute(
        select(CloudAccount).where(CloudAccount.user_id == user_id)
    )
    account_count = len(account_result.scalars().all())

    # Free tier: 1 account, Premium: unlimited
    if subscription and subscription.plan == "FREE" and account_count >= 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Free tier limited to 1 cloud account. Upgrade to Premium for unlimited accounts.",
        )


@router.post("/cloud-accounts", response_model=CloudAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_cloud_account(
    account_data: CloudAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect a cloud account for cost analysis."""
    await check_subscription_limit(current_user.id, db)

    # Validate provider
    valid_providers = ["AWS", "GCP", "AZURE"]
    if account_data.provider not in valid_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}",
        )

    # In production, validate credentials here before saving
    # For now, just store them

    account = CloudAccount(
        user_id=current_user.id,
        name=account_data.name,
        provider=account_data.provider,
        credentials=account_data.credentials,  # In production, encrypt this
        region=account_data.region,
        is_active=True,
    )

    db.add(account)
    await db.commit()
    await db.refresh(account)

    return account


@router.get("/cloud-accounts", response_model=List[CloudAccountResponse])
async def list_cloud_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's connected cloud accounts."""
    result = await db.execute(
        select(CloudAccount).where(CloudAccount.user_id == current_user.id)
    )
    accounts = result.scalars().all()
    return accounts


@router.get("/cloud-accounts/{account_id}", response_model=CloudAccountResponse)
async def get_cloud_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get cloud account details."""
    result = await db.execute(
        select(CloudAccount).where(
            CloudAccount.id == account_id,
            CloudAccount.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found",
        )

    return account


@router.delete("/cloud-accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cloud_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect a cloud account."""
    result = await db.execute(
        select(CloudAccount).where(
            CloudAccount.id == account_id,
            CloudAccount.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found",
        )

    await db.delete(account)
    await db.commit()

    return None


@router.post("/analyze", response_model=CostAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def run_cost_analysis(
    request: CostAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run cost analysis on a cloud account."""
    # Get cloud account
    result = await db.execute(
        select(CloudAccount).where(
            CloudAccount.id == request.cloud_account_id,
            CloudAccount.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloud account not found",
        )

    # Get cloud provider analyzer
    analyzer = get_analyzer(account.provider)

    # Fetch resources from cloud provider
    resources = analyzer.fetch_resources(account.credentials, account.region or "us-east-1")

    # Run AI cost analysis
    analysis_result = CostOptimizerEngine.analyze_resources(account.provider, resources)

    # Create cost analysis record
    cost_analysis = CostAnalysis(
        cloud_account_id=account.id,
        analysis_date=datetime.utcnow(),
        total_monthly_cost=analysis_result["total_monthly_cost"],
        potential_savings=analysis_result["potential_savings"],
        savings_percentage=analysis_result["savings_percentage"],
        resource_count=analysis_result["resource_count"],
        cost_breakdown=analysis_result["cost_breakdown"],
    )

    db.add(cost_analysis)
    await db.flush()

    # Create recommendation records
    for rec in analysis_result["recommendations"]:
        recommendation = CostRecommendation(
            cost_analysis_id=cost_analysis.id,
            resource_type=rec["resource_type"],
            resource_id=rec["resource_id"],
            recommendation_type=rec["recommendation_type"],
            title=rec["title"],
            description=rec["description"],
            current_cost=rec["current_cost"],
            estimated_new_cost=rec["estimated_new_cost"],
            monthly_savings=rec["monthly_savings"],
            annual_savings=rec["annual_savings"],
            priority=rec["priority"],
            implementation_effort=rec["implementation_effort"],
            status=rec["status"],
            recommendation_metadata=rec.get("metadata", {}),
        )
        db.add(recommendation)

    # Update last synced timestamp
    account.last_synced_at = datetime.utcnow()

    await db.commit()
    await db.refresh(cost_analysis)

    # Fetch recommendations to include in response
    rec_result = await db.execute(
        select(CostRecommendation).where(CostRecommendation.cost_analysis_id == cost_analysis.id)
    )
    cost_analysis.recommendations = rec_result.scalars().all()

    return cost_analysis


@router.get("/analyses", response_model=List[CostAnalysisResponse])
async def list_cost_analyses(
    cloud_account_id: uuid.UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List cost analyses."""
    if cloud_account_id:
        # Verify ownership
        account_result = await db.execute(
            select(CloudAccount).where(
                CloudAccount.id == cloud_account_id,
                CloudAccount.user_id == current_user.id,
            )
        )
        account = account_result.scalar_one_or_none()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cloud account not found",
            )

        query = select(CostAnalysis).where(CostAnalysis.cloud_account_id == cloud_account_id)
    else:
        # Get all analyses for user's accounts
        account_ids_result = await db.execute(
            select(CloudAccount.id).where(CloudAccount.user_id == current_user.id)
        )
        account_ids = [row[0] for row in account_ids_result.all()]

        query = select(CostAnalysis).where(CostAnalysis.cloud_account_id.in_(account_ids))

    result = await db.execute(query.order_by(CostAnalysis.analysis_date.desc()))
    analyses = result.scalars().all()

    # Load recommendations for each analysis
    for analysis in analyses:
        rec_result = await db.execute(
            select(CostRecommendation).where(CostRecommendation.cost_analysis_id == analysis.id)
        )
        analysis.recommendations = rec_result.scalars().all()

    return analyses


@router.get("/analyses/{analysis_id}", response_model=CostAnalysisResponse)
async def get_cost_analysis(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get cost analysis details."""
    result = await db.execute(
        select(CostAnalysis).where(CostAnalysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cost analysis not found",
        )

    # Verify ownership through cloud account
    account_result = await db.execute(
        select(CloudAccount).where(
            CloudAccount.id == analysis.cloud_account_id,
            CloudAccount.user_id == current_user.id,
        )
    )
    account = account_result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Load recommendations
    rec_result = await db.execute(
        select(CostRecommendation).where(CostRecommendation.cost_analysis_id == analysis.id)
    )
    analysis.recommendations = rec_result.scalars().all()

    return analysis


@router.patch("/recommendations/{recommendation_id}")
async def update_recommendation_status(
    recommendation_id: uuid.UUID,
    action: RecommendationActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Apply or dismiss a cost recommendation."""
    result = await db.execute(
        select(CostRecommendation).where(CostRecommendation.id == recommendation_id)
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    # Verify ownership through cost analysis -> cloud account
    analysis_result = await db.execute(
        select(CostAnalysis).where(CostAnalysis.id == recommendation.cost_analysis_id)
    )
    analysis = analysis_result.scalar_one_or_none()

    account_result = await db.execute(
        select(CloudAccount).where(
            CloudAccount.id == analysis.cloud_account_id,
            CloudAccount.user_id == current_user.id,
        )
    )
    account = account_result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    if action.action == "APPLY":
        recommendation.status = "APPLIED"
    elif action.action == "DISMISS":
        recommendation.status = "DISMISSED"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be APPLY or DISMISS",
        )

    await db.commit()

    return {"message": f"Recommendation {action.action.lower()}ed successfully"}
