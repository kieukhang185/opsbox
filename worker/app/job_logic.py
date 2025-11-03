import random
import time
from datetime import UTC, datetime, timedelta

from opsbox_common.database import SessionLocal
from opsbox_common.models import Task, TaskStatus
from sqlalchemy import delete


def run_task_imp(task_id: str) -> str:
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
        if random.random() < 0.5:
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


def cleanup_old_tasks_impl(retention_mins: int = 5) -> int:
    """Delete tasks older than N minutes. Returns number of rows deleted."""
    cutoff = datetime.now(UTC) - timedelta(minutes=retention_mins)  ##  5 minutes for testing
    db = SessionLocal()
    try:
        q = (
            delete(Task)
            .where(Task.created_at < cutoff)
            .where(Task.status.in_([TaskStatus.SUCCEEDED, TaskStatus.FAILED]))
        )
        res = db.execute(q)
        db.commit()

        deleted = res.rowcount if res.rowcount is not None and res.rowcount >= 0 else 0
        return deleted
    finally:
        db.close()
