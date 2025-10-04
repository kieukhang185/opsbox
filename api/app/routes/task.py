from typing import Annotated, TypeAlias
from uuid import UUID

from app.crud import task as task_crud
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from opsbox_common.database import get_db
from prometheus_client import Counter, Histogram
from sqlalchemy.orm import Session

# Define metrics
REQS = Counter("api_requests_total", "API requests", ["method", "path", "status"])
LAT = Histogram("api_request_latency_seconds", "API request latency", ["method", "path"])


DBSession: TypeAlias = Annotated[Session, Depends(get_db)]

route = APIRouter(prefix="/tasks", tags=["tasks"])


@route.post("", response_model=TaskOut)
def create_task(payload: TaskCreate, db: DBSession):
    return task_crud.create(db, payload)


@route.get("", response_model=list[TaskOut])
def list_tasks(db: DBSession):
    return task_crud.list_tasks(db)


@route.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: UUID, db: DBSession):
    task = task_crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@route.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: UUID, payload: TaskUpdate, db: DBSession):
    task = task_crud.update(db, task_id, payload)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@route.delete("/{task_id}", response_model=dict)
def delete_task(task_id: UUID, db: DBSession):
    status = task_crud.delete(db, task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "deleted"}


@route.post("/{task_id}/run", status_code=status.HTTP_201_CREATED)
def run_task_endpoint(task_id: UUID, db: DBSession):
    task = get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_crud.run_task(db, task_id)
