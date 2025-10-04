from typing import Any

from app.infra.kube import get_k8s_client
from fastapi import HTTPException, Query

NAMESPACE_DESC = Query(None, description="If omitted, lists across all namespaces")
LABEL_SELECTOR_DESC = Query(None, description="e.g. app=api,component=web")
LIMIT_DESC = Query(200, ge=1, le=2000)
CONTINUE_DESC = Query(None, description="Continue token from previous query")
INCLUDE_METRICS_DESC = Query(
    False, description="Join CPU/mem usage from metrics.k8s.io if available"
)


def _node_ready(conditions) -> bool:
    for c in conditions or []:
        if c.type == "Ready":
            return c.status == "True"
    return False


def _node_addr(status) -> dict[str, str | None]:
    bytype = {a.type: a.address for a in (status.addresses or [])}
    return {
        "internal": bytype.get("InternalIP"),
        "external": bytype.get("ExternalIP"),
        "hostname": bytype.get("Hostname"),
    }


def _node_summary(n) -> dict[str, Any]:
    s = n.status
    ni = s.node_info
    return {
        "name": n.metadata.name,
        "labels": n.metadata.labels or {},
        "taints": [
            {"key": t.key, "value": t.value, "effect": t.effect} for t in (n.spec.taints or [])
        ],
        "unschedulable": bool(getattr(n.spec, "unschedulable", False)),
        "ready": _node_ready(s.conditions),
        "addresses": _node_addr(s),
        "capacity": s.capacity,
        "allocatable": s.allocatable,
        "kubelet_version": getattr(ni, "kubelet_version", None),
        "os_image": getattr(ni, "os_image", None),
        "container_runtime": getattr(ni, "container_runtime_version", None),
        "kernel_version": getattr(ni, "kernel_version", None),
        "arch": getattr(ni, "architecture", None),
        "images": [{"names": i.names, "size_bytes": i.size_bytes} for i in (s.images or [])][
            :10
        ],  # top 10
        "conditions": [
            {
                "type": c.type,
                "status": c.status,
                "reason": c.reason,
                "message": c.message,
                "last_transition_time": c.last_transition_time,
            }
            for c in (s.conditions or [])
        ],
        "creation_timestamp": n.metadata.creation_timestamp,
    }


# ---------- list nodes ----------
def list_nodes(
    label_selector: str | None = None,
    field_selector: str | None = None,
    limit: int = LIMIT_DESC,
    _continue: str | None = CONTINUE_DESC,
    include_metrics: bool = INCLUDE_METRICS_DESC,
):
    k8s = get_k8s_client()
    v1 = k8s.CoreV1Api()
    res = v1.list_node(
        label_selector=label_selector,
        field_selector=field_selector,
        limit=limit,
        _continue=_continue,
    )
    items = [_node_summary(n) for n in res.items]

    if include_metrics:
        try:
            co = k8s.CustomObjectsApi()
            m = co.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
            usage_map = {i["metadata"]["name"]: i["usage"] for i in m.get("items", [])}
            for it in items:
                it["usage"] = usage_map.get(
                    it["name"]
                )  # cpu (e.g., "123m"), memory (e.g., "1024Mi")
        except Exception:
            # metrics-server not installed or RBAC missing; keep going without usage
            pass

    return {"items": items, "continue": res.metadata._continue}


# ---------- node detail ----------
def get_node(name: str):
    k8s = get_k8s_client()
    v1 = k8s.CoreV1Api()
    try:
        n = v1.read_node(name)
        return _node_summary(n)
    except k8s.exceptions.ApiException as e:  # type: ignore[attr-defined]
        if e.status == 404:
            raise HTTPException(status_code=404, detail="Node not found")
        raise


# ---------- node metrics only ----------
def get_node_metrics(name: str):
    k8s = get_k8s_client()
    co = k8s.CustomObjectsApi()
    try:
        data = co.get_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes", name)
        return data  # includes .usage.cpu and .usage.memory
    except k8s.exceptions.ApiException as e:  # type: ignore[attr-defined]
        if e.status == 404:
            raise HTTPException(
                status_code=404, detail="Metrics not found (is metrics-server installed?)"
            )
        raise


# ---------- pods scheduled on a node ----------
def list_node_pods(
    name: str,
    namespace: str | None = NAMESPACE_DESC,
    label_selector: str | None = LABEL_SELECTOR_DESC,
    limit: int = LIMIT_DESC,
    _continue: str | None = CONTINUE_DESC,
):
    k8s = get_k8s_client()
    v1 = k8s.CoreV1Api()
    field_selector = f"spec.nodeName={name}"
    if namespace:
        res = v1.list_namespaced_pod(
            namespace,
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
    # return minimal pod info for table
    items = [
        {
            "name": p.metadata.name,
            "namespace": p.metadata.namespace,
            "phase": p.status.phase,
            "start_time": p.status.start_time,
            "labels": p.metadata.labels or {},
        }
        for p in res.items
    ]
    return {"items": items, "continue": res.metadata._continue}
