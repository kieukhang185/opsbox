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
