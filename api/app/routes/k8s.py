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
    namespaces = k8s.list_namespaces()
    if namespace in namespaces:
        return {"namespace": namespace}
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
    pods = k8s.list_pods(namespace)
    if pod_name in pods:
        return {"pod": pod_name, "namespace": namespace}
    return {"error": "Pod not found"}
