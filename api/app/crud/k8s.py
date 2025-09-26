from app.infra.kube import get_k8s_client


def list_namespaces():
    k8s_client = get_k8s_client()
    v1 = k8s_client.CoreV1Api()
    namespaces = v1.list_namespace()
    return [ns.metadata.name for ns in namespaces.items]


def ns_info(namespace: str):
    k8s_client = get_k8s_client()
    v1 = k8s_client.CoreV1Api()
    ns = v1.read_namespace(name=namespace)
    return {
        "name": ns.metadata.name,
        "labels": ns.metadata.labels,
        "annotations": ns.metadata.annotations,
        "status": ns.status.phase,
        "creation_timestamp": ns.metadata.creation_timestamp,
        "uid": ns.metadata.uid,
        "resource_version": ns.metadata.resource_version,
        "self_link": ns.metadata.self_link,
        "finalizers": ns.metadata.finalizers,
        "spec": ns.spec.to_dict() if ns.spec else {},
        "status_details": ns.status.to_dict() if ns.status else {},
    }


def list_pods(namespace: str = "default"):
    k8s_client = get_k8s_client()
    v1 = k8s_client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace)
    return [pod.metadata.name for pod in pods.items]


def pod_info(namespace: str, pod_name: str):
    k8s_client = get_k8s_client()
    v1 = k8s_client.CoreV1Api()
    pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    if not pod:
        return {"error": "Pod not found"}
    return {
        "name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
        "labels": pod.metadata.labels,
        "annotations": pod.metadata.annotations,
        "status": pod.status.phase,
        "node_name": pod.spec.node_name if pod.spec else None,
        "host_ip": pod.status.host_ip if pod.status else None,
        "pod_ip": pod.status.pod_ip if pod.status else None,
        "start_time": pod.status.start_time if pod.status else None,
        "containers": (
            [container.to_dict() for container in pod.spec.containers] if pod.spec else []
        ),
        "creation_timestamp": pod.metadata.creation_timestamp,
        "uid": pod.metadata.uid,
        "resource_version": pod.metadata.resource_version,
        "self_link": pod.metadata.self_link,
        "finalizers": pod.metadata.finalizers,
        "spec": pod.spec.to_dict() if pod.spec else {},
        "status_details": pod.status.to_dict() if pod.status else {},
    }


def list_nodes():
    k8s_client = get_k8s_client()
    v1 = k8s_client.CoreV1Api()
    nodes = v1.list_node()
    return [node.metadata.name for node in nodes.items]


def node_info(node_name: str):
    k8s_client = get_k8s_client()
    v1 = k8s_client.CoreV1Api()
    node = v1.read_node(name=node_name)
    if not node:
        return {"error": "Node not found"}
    return {
        "name": node.metadata.name,
        "labels": node.metadata.labels,
        "annotations": node.metadata.annotations,
        "creation_timestamp": node.metadata.creation_timestamp,
        "uid": node.metadata.uid,
        "resource_version": node.metadata.resource_version,
        "self_link": node.metadata.self_link,
        "finalizers": node.metadata.finalizers,
        "spec": node.spec.to_dict() if node.spec else {},
        "status_details": node.status.to_dict() if node.status else {},
    }
