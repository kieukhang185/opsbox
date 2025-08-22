
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from .models import Task, TaskStatus
from .schemas import TaskUpdate


def create(db: Session, title: str) -> Task:
    task = Task(title=title, status=TaskStatus.NEW)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def list_tasks(db: Session) -> List[Task]:
    return db.query(Task).all()

def get_task(db: Session, task_id: UUID) -> Optional[Task]:
    return db.get(Task, task_id)

def update(db: Session, task_id: UUID, task_update: TaskUpdate) -> Optional[Task]:
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