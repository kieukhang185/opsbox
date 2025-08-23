from uuid import UUID

from opsbox_common.models import Task, TaskStatus
from sqlalchemy.orm import Session

from .schemas import TaskCreate, TaskUpdate


def create(db: Session, payload: TaskCreate) -> Task:
    task = Task(**payload.dict(), status=TaskStatus.NEW)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(db: Session) -> list[Task]:
    return db.query(Task).all()


def get_task(db: Session, task_id: UUID) -> Task | None:
    return db.get(Task, task_id)


def update(db: Session, task_id: UUID, task_update: TaskUpdate) -> Task | None:
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


def delete(db: Session, task_id: UUID) -> bool:
    task = get_task(db, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True
