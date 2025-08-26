from opsbox_common.celery_app import make_celery
from opsbox_common.settings import CELERY_QUEUE

celery_app = make_celery("opsbox")
celery_app.conf.task_default_queue = CELERY_QUEUE
