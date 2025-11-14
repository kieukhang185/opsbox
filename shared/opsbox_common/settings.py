# shared/opsbox_common/settings.py
import os

# DB
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@pg-postgresql.dev.svc.cluster.local:5432/postgres",
)

# Redis (broker + backend)
BROKER_URL = os.getenv("BROKER_URL", "amqp://opsbox:opsbox@rabbitmq.dev.svc.cluster.local:5672//")
CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND", "redis://:redis@redis-master.dev.svc.cluster.local:6379/1"
)

# Celery
QUEUE_NAME = os.getenv("QUEUE_NAME", "tasks")
CELERY_QUEUE = os.getenv("CELERY_QUEUE", "default")
CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "UTC")
CELERY_RESULT_TTL = int(os.getenv("CELERY_RESULT_TTL", "3600"))  # 1h default
CELERY_CONCURRENCY = int(os.getenv("CELERY_CONCURRENCY", "1"))  # tune per env
