from pydantic import BaseModel
from datetime import datetime
import uuid


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    actor_id: uuid.UUID
    action: str
    subject_type: str
    subject_id: uuid.UUID
    metadata: dict
    created_at: datetime

    class Config:
        from_attributes = True
