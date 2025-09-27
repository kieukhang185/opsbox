from fastapi import Query, HTTPException
from app.infra.kube import get_k8s_client
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta



def _pod(p) -> Dict[str, Any]:
    containers = p.spec.containers or []
    statuses = p.status.container_statuses or []
    cstate = []
    for i, c in enumerate(containers):
        st = statuses[i] if i < len(statuses) else None
        state_obj = getattr(st, "state", None)
        if state_obj and getattr(state_obj, "waiting", None):
            state = {"state": "Waiting", "reason": state_obj.waiting.reason, "message": state_obj.waiting.message}
        elif state_obj and getattr(state_obj, "terminated", None):
            t = state_obj.terminated
            state = {"state": "Terminated", "reason": t.reason, "exit_code": t.exit_code, "finished_at": t.finished_at}
        elif state_obj and getattr(state_obj, "running", None):
            state = {"state": "Running", "started_at": state_obj.running.started_at}
        else:
            state = {"state": "Unknown"}
        cstate.append({
            "name": c.name,
            "image": c.image,
            "ready": getattr(st, "ready", None),
            "restarts": getattr(st, "restart_count", 0),
            "state": state,
            "resources": {
                "requests": getattr(c.resources, "requests", None),
                "limits": getattr(c.resources, "limits", None),
            }
        })
    return {
        "name": p.metadata.name,
        "namespace": p.metadata.namespace,
        "node": p.spec.node_name,
        "phase": p.status.phase,
        "start_time": p.status.start_time,
        "labels": p.metadata.labels or {},
        "annotations": p.metadata.annotations or {},
        "qos_class": getattr(p.status, "qos_class", None),
        "containers": cstate,
        "host_ip": p.status.host_ip,
        "pod_ip": p.status.pod_ip,
    }


def get_pods(
    namespace: Optional[str] = Query(None, description="If omitted, lists across all namespaces"),
    label_selector: Optional[str] = Query(None, description="e.g. app=api,component=web"),
    field_selector: Optional[str] = Query(None, description="e.g. status.phase=Running"),
    limit: int = Query(200, ge=1, le=2000),
    _continue: Optional[str] = None,
):
    k8s = get_k8s_client()
    v1 = k8s.CoreV1Api()
    if namespace:
        res = v1.list_namespaced_pod(
            namespace=namespace,
            label_selector=label_selector,
            field_selector=field_selector,
            limit=limit,
            _continue=_continue,
        )
    else:
        res = v1.list_pod_for_all_namespaces(
            label_selector=label_selector,
            field_selector=field_selector,
            limit=limit,
            _continue=_continue,
        )
    return {
        "items": [_pod(p) for p in res.items],
        "continue": res.metadata._continue,
    }


def get_pod(namespace: str, name: str):
    k8s = get_k8s_client()
    v1 = k8s.CoreV1Api()
    try:
        p = v1.read_namespaced_pod(name=name, namespace=namespace)
        return _pod(p)
    except k8s.exceptions.ApiException as e:  # type: ignore[attr-defined]
        if e.status == 404:
            raise HTTPException(status_code=404, detail="Pod not found")
        raise


def get_pod_logs(
    namespace: str,
    name: str,
    container: Optional[str] = None,
    tail_lines: Optional[int] = Query(500, ge=1, le=10000),
    since_seconds: Optional[int] = Query(None, ge=1),
    previous: bool = Query(False, description="Get logs for previously terminated container"),
):
    """
    Security note: expose only if you intend to show logs in the UI.
    Consider RBAC/authorization at your API layer if needed.
    """
    k8s = get_k8s_client()
    v1 = k8s.CoreV1Api()
    try:
        data = v1.read_namespaced_pod_log(
            name=name,
            namespace=namespace,
            container=container,
            tail_lines=tail_lines,
            since_seconds=since_seconds,
            previous=previous,
            timestamps=True,
        )
        return {"container": container, "lines": data.splitlines()}
    except k8s.exceptions.ApiException as e:  # type: ignore[attr-defined]
        if e.status == 404:
            raise HTTPException(status_code=404, detail="Pod or container not found")
        raise
