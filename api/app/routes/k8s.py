from api.app.crud import k8s_events, k8s_nodes, k8s_pods
from fastapi import APIRouter, Query
from typing import Optional

from app.crud import k8s_ns

kubectl = APIRouter(prefix="/kubectl", tags=["kubectl"])


@kubectl.get("/namespaces")
def get_namespace(
    namespace: str,
    label_selector: Optional[str] | None,
    limit: Optional[int] | None,
    _continue: Optional[str] = None
):
    """
    Get details of a specific namespace.
    """
    namespace_info = k8s_ns.get_namespaces(namespace, label_selector, limit, _continue)
    if namespace_info:
        return namespace_info
    return {"error": "Namespace not found"}


@kubectl.get("/pods")
def list_pods(
    namespace: Optional[str] = Query(None, description="If omitted, lists across all namespaces"),
    label_selector: Optional[str] = Query(None, description="e.g. app=api,component=web"),
    field_selector: Optional[str] = Query(None, description="e.g. status.phase=Running"),
    limit: int = Query(200, ge=1, le=2000),
    _continue: Optional[str] = None,
):
    """
    List all pods in a specific namespace.
    """
    pods = k8s_pods.get_pods(namespace, label_selector, field_selector, limit, _continue)
    if pods:
        return pods
    return {"error": "Pod not found"}


@kubectl.get("/pods/{namespace}/{name}")
def get_pod(
    namespace: str,
    name: str,
):
    """
    Get details of a specific pod in a specific namespace.
    """
    pod = k8s_pods.get_pod(namespace, name)
    if pod:
        return pod
    return {"error": "Pod not found"}


@kubectl.get("/nodes")
def get_node(
    label_selector: Optional[str] = None,
    field_selector: Optional[str] = None,
    limit: int = Query(200, ge=1, le=2000),
    _continue: Optional[str] = None,
    include_metrics: bool = Query(False),
):
    """
    Get details of a specific node.
    """
    node_info = k8s_nodes.list_nodes(label_selector, field_selector, limit, _continue, include_metrics)
    if node_info:
        return node_info
    return {"error": "Nodes not found"}


@kubectl.get("/nodes/{name}")
def get_node(name: str):
    node = k8s_nodes.get_node(name)
    if node:
        return node
    return {"error": "Node not found"}


@kubectl.get("/nodes/{name}/metrics")
def get_node_metrics(name: str):
    node = k8s_nodes.get_node_metrics(name)
    if node:
        return node
    return {"error": "Node not found"}


@kubectl.get("/nodes/{name}/pods")
def list_node_pods(
    name: str,
    namespace: Optional[str] = Query(None),
    label_selector: Optional[str] = None,
    limit: int = Query(200, ge=1, le=2000),
    _continue: Optional[str] = None,
):
    node = k8s_nodes.list_node_pods(name, namespace, label_selector, limit, _continue)
    if node:
        return node
    return {"error": "Node not found"}


@kubectl.get("/events")
def list_events(
    namespace: Optional[str] = Query("default"),
    label_selector: Optional[str] = None,
    field_selector: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    _continue: Optional[str] = None,
    since_seconds: Optional[str] = Query(None, ge=1),
    since_time: Optional[str] = Query(None),
    only_warning: bool = Query(False)
):
    """
    Get events of a specific namespace if provide or all namespace
    """
    return k8s_events.list_events(
        namespace,
        label_selector,
        field_selector,
        limit,
        _continue,
        since_seconds,
        since_time,
        only_warning
    )
