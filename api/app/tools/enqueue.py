import os

from redis import Redis
from rq import Queue

REDIS_URL = os.getenv("REDIS_URL", "redis://redis-master.dev.svc.cluster.local:6379/0")
QUEUE_NAME = os.getenv("QUEUE_NAME", "default")

# Enqueue by STRING import path; worker will import it when executing:
#   opsbox.worker.app.worker.run_task
q = Queue(QUEUE_NAME, connection=Redis.from_url(REDIS_URL))
job = q.enqueue("app.worker.run_task", "c5256521-69a3-43e8-9748-6f033cd4a3af")

print(job.get_id())
