from kubernetes import client, config


def get_k8s_client():
    try:
        # running inside a Pod
        config.load_incluster_config()
    except config.ConfigException:
        # running locally
        config.load_kube_config()
    return client
