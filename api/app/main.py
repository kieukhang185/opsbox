import time

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from opsbox_common.database import init_db
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.routes.k8s import kubectl
from app.routes.task import LAT, REQS
from app.routes.task import route as task

app = FastAPI(
    title="OpsBox API",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.include_router(task)
app.include_router(kubectl)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # ["*"] for dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "*"],
    expose_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
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
