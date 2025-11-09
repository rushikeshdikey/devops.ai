from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"ok": True, "version": "1.0.0"}


@router.get("/metrics")
async def metrics():
    """Basic metrics endpoint."""
    # In a real system, this would return actual metrics
    return {
        "requests_total": 0,
        "validations_total": 0,
    }
