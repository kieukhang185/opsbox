from typing import Annotated, TypeAlias
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status
from opsbox_common.database import get_db, init_db
from sqlalchemy.orm import Session

from . import crud
from .schemas import TaskCreate, TaskOut, TaskUpdate

app = FastAPI(
    title="OpsBox API",
)


@app.on_event("startup")
def on_startup():
    # For dev/test convenience. In production use Alembic.
    init_db()


DBSession: TypeAlias = Annotated[Session, Depends(get_db)]


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.post("/tasks/", response_model=TaskOut)
def create_task(payload: TaskCreate, db: DBSession):
    return crud.create(db, payload)


@app.get("/tasks/", response_model=list[TaskOut])
def list_tasks(db: DBSession):
    return crud.list_tasks(db)


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: UUID, db: DBSession):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: UUID, payload: TaskUpdate, db: DBSession):
    task = crud.update(db, task_id, payload)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: UUID, db: DBSession):
    status = crud.delete(db, task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return None


@app.post("/tasks/{task_id}/run", status_code=status.HTTP_201_CREATED)
def run_task_endpoint(task_id: UUID, db: DBSession):
    task = get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.run_task(db, task_id)
