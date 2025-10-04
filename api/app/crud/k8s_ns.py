from datetime import datetime
from typing import Any

from app.infra.kube import get_k8s_client
from fastapi import Query

LIMIT_DESC = Query(200, ge=1, le=2000)
CONTINUE_DESC = Query(None, description="Continue token from previous query")


def _ns(item) -> dict[str, Any]:
    s = getattr(item, "status", None)
    return {
        "name": item.metadata.name,
        "status": getattr(s, "phase", None) or getattr(s, "phase", "Active"),
        "labels": item.metadata.labels or {},
        "annotations": item.metadata.annotations or {},
        "creation_timestamp": item.metadata.creation_timestamp,
        "age_seconds": (
            int(
                (
                    datetime.utcnow() - item.metadata.creation_timestamp.replace(tzinfo=None)
                ).total_seconds()
            )
            if item.metadata.creation_timestamp
            else None
        ),
    }


def get_namespaces(
    namespace: str | None = None,
    label_selector: str | None = None,
    limit: int = LIMIT_DESC,
    _continue: str | None = CONTINUE_DESC,
):
    k8s = get_k8s_client()
    v1 = k8s.CoreV1Api()

    if namespace:
        res = v1.list_namespace(
            name=namespace, label_selector=label_selector, limit=limit, _continue=_continue
        )
    else:
        res = v1.list_namespace(label_selector=label_selector, limit=limit, _continue=_continue)

    return {
        "items": [_ns(n) for n in res.items],
        "continue": res.metadata._continue,
    }
