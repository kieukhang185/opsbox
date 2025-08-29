import threading
from wsgiref.simple_server import make_server

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)

# Define metrics
registry = CollectorRegistry()
JOBS = Counter("worker_jobs_total", "Total number of jobs", ["result"], registry=registry)
JOB_LATENCY = Histogram("worker_job_latency_seconds", "Job latency in seconds", registry=registry)
CLEANUPS = Counter("worker_cleanups_total", "Total number of cleanups", registry=registry)


def metrics_app(environ, start_response):
    data = generate_latest(registry)
    start_response("200 OK", [("Content-Type", CONTENT_TYPE_LATEST)])
    return [data]


def start_metrics_server(port: int = 9090):
    server = make_server("", port, metrics_app)
    thread = threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, thread
