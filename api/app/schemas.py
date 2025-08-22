from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .models import TaskStatus


class TaskBase(BaseModel):
    title: str | None = None

    class Config:
        from_attributes = True


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    status: TaskStatus | None = None
    result: str | None = None


class TaskOut(BaseModel):
    id: UUID
    title: str | None
    created_at: datetime
    status: TaskStatus | None
    result: str | None = None

    class Config:
        from_attributes = True
