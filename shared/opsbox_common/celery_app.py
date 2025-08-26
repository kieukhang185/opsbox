# shared/opsbox_common/celery_app.py
from celery import Celery

from .settings import BROKER_URL, CELERY_RESULT_TTL, CELERY_TIMEZONE, RESULT_BACKEND


def make_celery(app_name: str = "opsbox") -> Celery:
    c = Celery(app_name, broker=BROKER_URL, backend=RESULT_BACKEND)
    c.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone=CELERY_TIMEZONE,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        result_expires=CELERY_RESULT_TTL,
    )
    return c
