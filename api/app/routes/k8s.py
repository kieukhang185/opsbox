from fastapi import APIRouter, Query

from app.crud import k8s

kubectl = APIRouter(prefix="/kubectl", tags=["kubectl"])


@kubectl.get("/namespaces")
def list_namespaces():
    """
    List all namespaces in the Kubernetes cluster.
    """
    return k8s.list_namespaces()


@kubectl.get("/namespaces/{namespace}")
def get_namespace(namespace: str):
    """
    Get details of a specific namespace.
    """
    namespace_info = k8s.ns_info(namespace)
    if namespace_info:
        return namespace_info
    return {"error": "Namespace not found"}


@kubectl.get("/pods")
def list_pods(namespace: str | None = Query("default")):
    """
    List all pods in a specific namespace.
    """
    return k8s.list_pods(namespace)


@kubectl.get("/pods/{pod_name}")
def get_pod(pod_name: str, namespace: str | None = Query("default")):
    """
    Get details of a specific pod in a specific namespace.
    """
    pod = k8s.pod_info(namespace, pod_name)
    if pod:
        return pod
    return {"error": "Pod not found"}


@kubectl.get("/nodes")
def get_nodes():
    """
    List all nodes in the Kubernetes cluster.
    """
    return k8s.list_nodes()


@kubectl.get("/nodes/{node_name}")
def get_node(node_name: str):
    """
    Get details of a specific node.
    """
    node_info = k8s.node_info(node_name)
    if node_info:
        return node_info
    return {"error": "Node not found"}
