from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from .models import TaskStatus

class TaskBase(BaseModel):
    title: Optional[str] = None

    class Config:
        from_attributes = True

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    status: Optional[TaskStatus] = None
    result: Optional[str] = None

class TaskOut(BaseModel):
    id: UUID
    title: Optional[str]
    created_at: datetime
    status: Optional[TaskStatus]
    result: Optional[str] = None

    class Config:
        from_attributes = True
