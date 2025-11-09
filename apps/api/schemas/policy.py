from pydantic import BaseModel
from datetime import datetime
import uuid


class PolicyCreate(BaseModel):
    name: str
    scope: str  # GLOBAL, PROJECT
    type: str = "OPA_MOCK"
    rule: str
    project_id: uuid.UUID | None = None


class PolicyResponse(BaseModel):
    id: uuid.UUID
    name: str
    scope: str
    type: str
    rule: str
    project_id: uuid.UUID | None
    created_at: datetime

    class Config:
        from_attributes = True


class PolicyValidateRequest(BaseModel):
    rule: str
    content: str
    type: str  # K8S_YAML, TERRAFORM, GENERIC_YAML
