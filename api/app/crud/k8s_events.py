from app.infra.kube import get_k8s_client
from typing import Optional, Dict, Any, List
from fastapi import Query
from datetime import datetime, timezone, timedelta


def _event_to_dict(e) -> Dict[str, Any]:
    meta = e.metadata
    involved = e.involved_object

    when = e.last_timestamp or (getattr(e, "event_time", None)) or (
        getattr(e, "series", None).last_observed_time if getattr(e, "series", None) else None
    )

    return {
        "name": meta.name,
        "namespace": meta.namespace,
        "type": e.type,            # Normal | Warning
        "reason": e.reason,        # e.g., BackOff
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
        "reporting_controller": getattr(e, "reporting_component", None) or getattr(e, "reporting_controller", None),
        "reporting_instance": getattr(e, "reporting_instance", None),
    }

def _parse_since_time(since_time: Optional[str]) -> Optional[datetime]:
    if not since_time:
        return None
    # Accept ISO8601 like "2025-09-26T04:00:00Z"
    return datetime.fromisoformat(since_time.replace("Z", "+00:00")).astimezone(timezone.utc)

def list_events(
    namespace: Optional[str] = Query(None, description="If set, get this namespace only"),
    label_selector: Optional[str] = None,
    field_selector: Optional[str] = Query(
        None,
        description="e.g. involvedObject.kind=Pod,involvedObject.name=my-pod" or "type=Warning"
    ),
    limit: int = Query(100, ge=1, le=1000),
    _continue: Optional[str] = None,
    since_seconds: Optional[str] = Query(None, ge=1, description="Return events newer than now - N seconds"),
    since_time: Optional[str] = Query(None, description='ISO8601, e.g. "2025-09-26T04:00:00Z"'),
    only_warning: bool = Query(False, description="Filter to type=Warning"),
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

    items: List[Dict[str, Any]] = [_event_to_dict(e) for e in res.items]

    cutoff: Optional[datetime] = None
    if since_seconds:
        cutoff = datetime.now(timezone.utc) if since_seconds == 0 else datetime.now(timezone.utc)
        cutoff = cutoff.replace(microsecond=0)  # cosmetic
        cutoff = cutoff - timedelta(seconds=since_seconds)
    elif since_time:
        cutoff = _parse_since_time(since_time)

    if cutoff:
        def newer(d: Dict[str, Any]) -> bool:
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
