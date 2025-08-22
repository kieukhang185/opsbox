from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .models import TaskStatus


class TaskBase(BaseModel):
    title: str | None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    status: TaskStatus | None
    result: str | None


class TaskOut(BaseModel):
    id: UUID
    title: str | None
    created_at: datetime
    status: TaskStatus | None
    result: str | None

    model_config = ConfigDict(from_attributes=True)
