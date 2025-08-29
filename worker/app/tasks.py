import os

from celery.schedules import crontab

from .celery_app import celery_app
from .job_logic import cleanup_old_tasks_impl, run_task_imp
from .metrics import CLEANUPS

RETENTION_MINUTES = int(os.getenv("RETENTION_MINUTES", "5"))


@celery_app.task(name="tasks.run_task")
def run_task(task_id: str) -> str:
    """Simulate work and update DB row."""
    return run_task_imp(task_id)


@celery_app.task(name="tasks.cleanup_old_tasks")
def cleanup_old_tasks() -> int:
    n = cleanup_old_tasks_impl(RETENTION_MINUTES)
    CLEANUPS.inc(n)
    return n


# Configure Beat schedule (hourly). You can change to every N minutes if desired.
celery_app.conf.beat_schedule = {
    "five-minutes-cleanup-old-tasks": {
        "task": "tasks.cleanup_old_tasks",
        "schedule": crontab(minute="*/5"),  # every 5 min
        "options": {"queue": os.getenv("QUEUE_NAME", "default")},
    }
}
