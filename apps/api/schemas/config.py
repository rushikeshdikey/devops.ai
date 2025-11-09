from pydantic import BaseModel
from datetime import datetime
import uuid


class ConfigCreate(BaseModel):
    title: str
    type: str  # K8S_YAML, TERRAFORM, GENERIC_YAML
    tags: list[str] = []


class ConfigResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    type: str
    latest_version_id: uuid.UUID | None
    tags: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ConfigVersionCreate(BaseModel):
    content: str


class ConfigVersionResponse(BaseModel):
    id: uuid.UUID
    config_id: uuid.UUID
    version_number: int
    content: str
    checksum: str
    created_by_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
