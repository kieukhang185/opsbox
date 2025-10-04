import datetime
from typing import Any

from fastapi import Query

from app.infra.kube import get_k8s_client

NAMESPACE_DESC = Query(None, description="If set, get this namespace only")
FIELD_SELECTOR_DESC = Query(
    None, description="e.g. involvedObject.kind=Pod,involvedObject.name=my-pod" or "type=Warning"
)
LIMIT_DESC = Query(100, ge=1, le=1000)
CONTINUE_DESC = Query(None, description="Continue token from previous query")
SINCE_SECOND_DESC = Query(None, ge=1, description="Return events newer than now - N seconds")
SINCE_TIME_DESC = Query(
    None, description='Return events newer than this time, e.g. "2025-09-26T04:00:00Z"'
)
ONLY_WARNING_DESC = Query(False, description="Filter to type=Warning")


def _event_to_dict(e) -> dict[str, Any]:
    meta = e.metadata
    involved = e.involved_object

    return {
        "name": meta.name,
        "namespace": meta.namespace,
        "type": e.type,  # Normal | Warning
        "reason": e.reason,  # e.g., BackOff
        "message": e.message,
        "count": e.count,
        "first_timestamp": e.first_timestamp,
        "last_timestamp": e.last_timestamp,
        "event_time": getattr(e, "event_time", None),
        "involved_object": {
            "kind": involved.kind,
            "name": involved.name,
            "namespace": involved.namespace,
            "uid": involved.uid,
            "fieldPath": involved.field_path,
        },
        "source": {
            "component": getattr(e.source, "component", None),
            "host": getattr(e.source, "host", None),
        },
        "reporting_controller": getattr(e, "reporting_component", None)
        or getattr(e, "reporting_controller", None),
        "reporting_instance": getattr(e, "reporting_instance", None),
    }


def _parse_since_time(since_time: str | None) -> datetime.datetime | None:
    if not since_time:
        return None
    # Accept ISO8601 like "2025-09-26T04:00:00Z"
    return datetime.datetime.fromisoformat(since_time.replace("Z", "+00:00")).astimezone(
        datetime.UTC
    )


def list_events(
    namespace: str | None = NAMESPACE_DESC,
    label_selector: str | None = None,
    field_selector: str | None = FIELD_SELECTOR_DESC,
    limit: int = LIMIT_DESC,
    _continue: str | None = CONTINUE_DESC,
    since_seconds: str | None = SINCE_SECOND_DESC,
    since_time: str | None = SINCE_TIME_DESC,
    only_warning: bool = ONLY_WARNING_DESC,
):
    k8s_client = get_k8s_client()
    v1 = k8s_client.CoreV1Api()

    fs = field_selector
    if only_warning:
        fs = f"type=Warning{',' + field_selector if field_selector else ''}"

    if namespace:
        res = v1.list_namespaced_event(
            namespace=namespace,
            label_selector=label_selector,
            field_selector=fs,
            limit=limit,
            _continue=_continue,
        )
    else:
        res = v1.list_event_for_all_namespaces(
            label_selector=label_selector,
            field_selector=fs,
            limit=limit,
            _continue=_continue,
        )

    items: list[dict[str, Any]] = [_event_to_dict(e) for e in res.items]

    cutoff: datetime.datetime | None = None
    if since_seconds:
        cutoff = (
            datetime.datetime.now(datetime.UTC)
            if since_seconds == 0
            else datetime.datetime.now(datetime.UTC)
        )
        cutoff = cutoff.replace(microsecond=0)  # cosmetic
        cutoff = cutoff - datetime.timedelta(seconds=since_seconds)
    elif since_time:
        cutoff = _parse_since_time(since_time)

    if cutoff:

        def newer(d: dict[str, Any]) -> bool:
            for k in ("last_timestamp", "event_time", "first_timestamp"):
                t = d.get(k)
                if t:
                    # k8s python client returns datetime objects already
                    tt = t if isinstance(t, datetime) else _parse_since_time(str(t))
                    if tt and tt >= cutoff:
                        return True
            return False

        items = [d for d in items if newer(d)]

    return {"items": items, "continue": res.metadata._continue}
