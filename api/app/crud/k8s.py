from app.infra.kube import get_k8s_client


def list_namespaces():
    k8s_client = get_k8s_client()
    v1 = k8s_client.CoreV1Api()
    namespaces = v1.list_namespace()
    return [ns.metadata.name for ns in namespaces.items]


def list_pods(namespace: str = "default"):
    k8s_client = get_k8s_client()
    v1 = k8s_client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace)
    return [pod.metadata.name for pod in pods.items]
