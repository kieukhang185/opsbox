from opsbox_common.celery_app import make_celery
from opsbox_common.settings import CELERY_QUEUE

celery_client = make_celery("opsbox")


def enqueue_run_task(task_id: str) -> str:
    r = celery_client.send_task("tasks.run_task", args=[task_id], queue=CELERY_QUEUE)
    return r.id
