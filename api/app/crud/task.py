from typing import Annotated, TypeAlias
from uuid import UUID

from fastapi import Depends
from opsbox_common.database import get_db
from opsbox_common.models import Task, TaskStatus
from sqlalchemy.orm import Session

from app.run_queue import enqueue_run_task
from app.schemas import TaskCreate, TaskUpdate

DBSession: TypeAlias = Annotated[Session, Depends(get_db)]


def create(db: DBSession, payload: TaskCreate) -> Task:
    task = Task(**payload.dict(), status=TaskStatus.NEW)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(db: DBSession) -> list[Task]:
    return db.query(Task).all()


def get_task(db: DBSession, task_id: UUID) -> Task | None:
    return db.get(Task, task_id)


def update(db: DBSession, task_id: UUID, task_update: TaskUpdate) -> Task | None:
    task = get_task(db, task_id)
    if not task:
        return None
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.result is not None:
        task.result = task_update.result
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete(db: DBSession, task_id: UUID) -> bool:
    task = get_task(db, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True


def run_task(db: DBSession, task_id: UUID) -> dict:
    # TODO: check worker status, if not running raise error
    task = get_task(db, task_id)
    if not task:
        raise ValueError(404, "Task not found")
    if task.status in {TaskStatus.RUNNING, TaskStatus.SUCCEEDED, TaskStatus.FAILED}:
        raise ValueError(409, f"Task already {task.status}")

    job_id = enqueue_run_task(task_id)
    return {"job_id": job_id, "task_id": task_id}
