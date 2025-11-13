import os
import time

from celery import Celery, signals
from opsbox_common.celery_app import make_celery
from opsbox_common.settings import CELERY_QUEUE

from .metrics import JOB_LATENCY, JOBS, start_metrics_server

BROKER_URL = os.getenv("BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
celery_app = Celery("opsbox", broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery_app.conf.task_default_queue = os.getenv("CELERY_QUEUE", "tasks")

celery_app = make_celery("opsbox")
celery_app.conf.task_default_queue = CELERY_QUEUE

if os.getenv("METRICS_PORT", "9090"):
    start_metrics_server(int(os.getenv("METRICS_PORT", "9090")))

_task_start_times = {}


@signals.task_prerun.connect
def _task_start(sender=None, task_id=None, **__):
    _task_start_times[task_id] = time.perf_counter()


@signals.task_postrun.connect
def _task_end(sender=None, task_id=None, state=None, **__):
    start = _task_start_times.pop(task_id, None)
    if start is not None:
        JOB_LATENCY.observe(time.perf_counter() - start)
    JOBS.labels((state or "unknown").lower()).inc()
