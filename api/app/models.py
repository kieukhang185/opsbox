import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class TaskStatus(enum.Enum):
    NEW = "new"
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Task(Base):
    __tablename__ = "task"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), index=True)
    status = Column(Enum(TaskStatus, name="task_status"), default=TaskStatus.NEW, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    result = Column(String(255), default=None, nullable=True)
