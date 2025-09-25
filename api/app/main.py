import time

from fastapi import FastAPI, Response
from opsbox_common.database import init_db
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.routes.task import LAT, REQS, route

app = FastAPI(
    title="OpsBox API",
)

app.include_router(route)


@app.on_event("startup")
def on_startup():
    # For dev/test convenience. In production use Alembic.
    init_db()


# Create middleware records
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    # use route.path if available to avoid high-cardinality URLs
    path = getattr(request.scope.get("route"), "path", request.url.path)
    REQS.labels(request.method, path, str(response.status_code)).inc()
    LAT.labels(request.method, path).observe(duration)
    return response


@app.get("/health")
def read_health():
    return {"status": "ok"}


@app.get("/metrics")
def read_metrics():
    """Metrics endpoint exposes value in Prometheus format"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
