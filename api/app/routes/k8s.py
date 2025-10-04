from fastapi import APIRouter, Query

from api.app.crud import k8s_events, k8s_nodes, k8s_ns, k8s_pods

kubectl = APIRouter(prefix="/kubectl", tags=["kubectl"])


NAMESPACE_DESC = Query(None, description="If set, get this namespace only")
LABEL_SELECTOR_DESC = Query(None, description="e.g. app=api,component=web")
FIELD_SELECTOR_DESC = Query(None, description="e.g. status.phase=Running")
LIMIT_DESC = Query(200, ge=1, le=2000)
CONTINUE_DESC = Query(None, description="Continue token from previous query")
SINCE_SECONDS_DESC = Query(None, ge=1, description="Return events newer than now - N seconds")
SINCE_TIME_DESC = Query(
    None, description='Return events newer than this time, e.g. "2025-09-26T04:00:00Z"'
)
ONLY_WARNING_DESC = Query(False, description="Filter to type=Warning")
INCLUDE_METRICS_DESC = Query(
    False, description="Join CPU/mem usage from metrics.k8s.io if available"
)


@kubectl.get("/namespaces")
def get_namespace(
    namespace: str | None = NAMESPACE_DESC,
    label_selector: str | None = LABEL_SELECTOR_DESC,
    limit: int | None = LIMIT_DESC,
    _continue: str | None = CONTINUE_DESC,
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
    namespace: str | None = NAMESPACE_DESC,
    label_selector: str | None = LABEL_SELECTOR_DESC,
    field_selector: str | None = FIELD_SELECTOR_DESC,
    limit: int = LIMIT_DESC,
    _continue: str | None = CONTINUE_DESC,
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
def get_nodes(
    label_selector: str | None = LABEL_SELECTOR_DESC,
    field_selector: str | None = FIELD_SELECTOR_DESC,
    limit: int = LIMIT_DESC,
    _continue: str | None = CONTINUE_DESC,
    include_metrics: bool = INCLUDE_METRICS_DESC,
):
    """
    Get details of a specific node.
    """
    node_info = k8s_nodes.list_nodes(
        label_selector, field_selector, limit, _continue, include_metrics
    )
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
    namespace: str | None = NAMESPACE_DESC,
    label_selector: str | None = LABEL_SELECTOR_DESC,
    limit: int = LIMIT_DESC,
    _continue: str | None = CONTINUE_DESC,
):
    node = k8s_nodes.list_node_pods(name, namespace, label_selector, limit, _continue)
    if node:
        return node
    return {"error": "Node not found"}


@kubectl.get("/events")
def list_events(
    namespace: str | None = NAMESPACE_DESC,
    label_selector: str | None = LABEL_SELECTOR_DESC,
    field_selector: str | None = FIELD_SELECTOR_DESC,
    limit: int = LIMIT_DESC,
    _continue: str | None = CONTINUE_DESC,
    since_seconds: str | None = SINCE_SECONDS_DESC,
    since_time: str | None = SINCE_TIME_DESC,
    only_warning: bool = ONLY_WARNING_DESC,
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
        only_warning,
    )
