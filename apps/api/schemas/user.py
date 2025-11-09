from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    role: str
