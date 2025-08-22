from fastapi import FastAPI, HTTPException, Depends, status
from contextlib import asynccontextmanager
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from .schemas import TaskOut, TaskCreate, TaskUpdate
from . import crud
from .database import get_db, init_db


app = FastAPI(
    title="OpsBox API",
)

@app.on_event("startup")
def on_startup():
    # For dev/test convenience. In production use Alembic.
    init_db()

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.post("/tasks/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload :  TaskCreate, db : Session = Depends(get_db)):
    return crud.create(db, title=payload.title)

@app.get("/tasks/", response_model=List[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    return crud.list_tasks(db)

@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: UUID, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: UUID, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = crud.update(db, task_id, payload)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, db: Session = Depends(get_db)):
    status = crud.delete(db, task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return None
