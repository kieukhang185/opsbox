import time
from typing import Annotated, TypeAlias
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Response, status
from opsbox_common.database import get_db, init_db
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy.orm import Session

from . import crud
from .schemas import TaskCreate, TaskOut, TaskUpdate

# Define metrics
REQS = Counter("api_requests_total", "API requests", ["method", "path", "status"])
LAT = Histogram("api_request_latency_seconds", "API request latency", ["method", "path"])

app = FastAPI(
    title="OpsBox API",
)


@app.on_event("startup")
def on_startup():
    # For dev/test convenience. In production use Alembic.
    init_db()


DBSession: TypeAlias = Annotated[Session, Depends(get_db)]


# Create middleware records
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    # use route.path if available to avoid high-cardinality URLs
    path = getattr(request.scope.get("route"), "path", request.url.path)
    REQS.labels(request.method, path, str(response.status_code)).inc()
    LAT.labels(request.method, path).observe(duration)
    return response


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.post("/tasks/", response_model=TaskOut)
def create_task(payload: TaskCreate, db: DBSession):
    return crud.create(db, payload)


@app.get("/metrics")
def read_metrics():
    """Metrics endpoint exposes value in Prometheus format"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


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
    return {"status": "deleted"}


@app.post("/tasks/{task_id}/run", status_code=status.HTTP_201_CREATED)
def run_task_endpoint(task_id: UUID, db: DBSession):
    task = get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.run_task(db, task_id)
