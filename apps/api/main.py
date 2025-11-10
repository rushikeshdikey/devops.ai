from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.core.config import get_settings
from apps.api.routers import (
    auth,
    users,
    projects,
    configs,
    validation,
    policies,
    audit,
    health,
    billing,
    cost_optimizer,
)

settings = get_settings()

app = FastAPI(
    title="DevOps Automation & Cost Optimizer API",
    description="API for DevOps configuration management, validation, and cloud cost optimization",
    version="2.0.0",
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
app.include_router(projects.router, prefix="/api")
app.include_router(configs.router, prefix="/api")
app.include_router(validation.router, prefix="/api")
app.include_router(policies.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(cost_optimizer.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "DevOps Automation API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
