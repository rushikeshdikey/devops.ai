from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.core.config import get_settings
from apps.api.routers import (
    auth,
    users,
    health,
    billing,
    cost_optimizer,
)

settings = get_settings()

app = FastAPI(
    title="Cloud Cost Optimizer API",
    description="AI-powered cloud cost optimization and savings recommendations",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGIN, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(cost_optimizer.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Cloud Cost Optimizer API",
        "version": "1.0.0",
        "description": "AI-powered cloud cost optimization",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
