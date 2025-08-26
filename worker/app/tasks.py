import random
import time
from datetime import UTC, datetime

from opsbox_common.database import SessionLocal
from opsbox_common.models import Task, TaskStatus

from .celery_app import celery_app


@celery_app.task(name="tasks.run_task")
def run_task(task_id: str) -> str:
    """Simulate work and update DB row."""
    db = SessionLocal()
    try:
        task = db.get(Task, task_id)
        if not task:
            return "Task not found"

        # mark running (idempotent)
        task.status = TaskStatus.RUNNING
        db.add(task)
        db.commit()

        time.sleep(random.uniform(0.5, 1.5))
        if random.random() < 0.85:
            task.status = TaskStatus.SUCCEEDED
            task.result = f"Processed at {datetime.now(UTC).isoformat()}"
        else:
            task.status = TaskStatus.FAILED
            task.result = "simulated failure"
        db.add(task)
        db.commit()
        return task.result or "ok"
    finally:
        db.close()
