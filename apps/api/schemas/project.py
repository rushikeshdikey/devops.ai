from pydantic import BaseModel
from datetime import datetime
import uuid


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_by_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
