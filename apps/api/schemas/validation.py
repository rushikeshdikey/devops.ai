from pydantic import BaseModel
from datetime import datetime
import uuid


class ValidationIssue(BaseModel):
    level: str  # ERROR, WARN, INFO
    code: str
    message: str
    path: str | None = None


class ValidationReport(BaseModel):
    status: str  # PASS, FAIL, WARN
    issues: list[ValidationIssue] = []


class ValidationRunResponse(BaseModel):
    id: uuid.UUID
    config_version_id: uuid.UUID
    status: str
    report: dict
    created_at: datetime

    class Config:
        from_attributes = True


class DryRunResponse(BaseModel):
    success: bool
    summary: str
    changed_resources: int
    diff_summary: str
