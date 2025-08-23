import random
import time
import traceback
from datetime import UTC, datetime
from uuid import UUID

from redis import Redis
from rq import Queue, Worker
from sqlalchemy.exc import SQLAlchemyError

from api.app.database import QUEUE_NAME, REDIS_URL, SessionLocal
from api.app.models import Task, TaskStatus


def run_task(task_id: UUID) -> str:
    """Simulate work and update DB."""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return f"Task {task_id} not found"

        task.status = TaskStatus.IN_PROGRESS
        db.add(task)
        db.commit()

        # Simulate work
        time.sleep(random.uniform(0.5, 1.5))

        if random.random() < 0.8:  # 80% chance to fail
            task.status = TaskStatus.COMPLETED
            task.result = f"Processed at {datetime.now(UTC).isoformat()}"
        else:
            raise RuntimeError("Simulated unexpected error")

        db.add(task)
        db.commit()
        return task.result or "ok"
    except Exception as e:
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = TaskStatus.FAILED
                task.result = f"error: {e}"
                db.add(task)
                db.commit()
        except SQLAlchemyError:
            pass
        traceback.print_exc()
        return f"failed: {e}"
    finally:
        db.close()


def main():
    conn = Redis.from_url(REDIS_URL)
    q = Queue(QUEUE_NAME, connection=conn)
    w = Worker([q], connection=conn)
    w.work(with_scheduler=True)


if __name__ == "__main__":
    main()
