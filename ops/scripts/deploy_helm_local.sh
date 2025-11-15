#!/usr/bin/env bash

# Deploy Helm charts locally
# within a kind Kubernetes cluster.
#
# Usage: deploy_helm_local.sh \
#   --api-image <api_image> \
#   --worker-image <worker_image> \
#   --k8s-namespace <namespace> \
#   --kind-cluster-name <cluster_name> [--monitoring]

set -Eeuo pipefail

API_IMG=""
K8S_NAMESPACE=""
KIND_CLUSTER_NAME=""
WORKER_IMG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -api|--api-image)
            api_image="$2"
            shift 2 ;;
        -k|--k8s-namespace)
            k8s_namespace="$2"
            shift 2 ;;
        -c|--kind-cluster-name)
            kind_cluster_name="$2"
            shift 2 ;;
        -worker|--worker-image)
            worker_image="$2"
            shift 2 ;;
        *)
            log_warn "Unknown option: $1"
            exit 1;;
    esac
done

API_IMG="${api_image}"
K8S_NAMESPACE="${k8s_namespace}"
KIND_CLUSTER_NAME="${kind_cluster_name}"
WORKER_IMG="${worker_image}"


build_images(){
    log_info "Building Docker images..."
    exist_image "${API_IMG}" || docker build -f api/Dockerfile -t "${API_IMG}" .
    exist_image "${WORKER_IMG}" || docker build -f worker/Dockerfile -t "${WORKER_IMG}" .
}

load_images_into_kind(){
    log_info "Loading images into kind cluster ${KIND_CLUSTER_NAME}..."
    kind load docker-image "${API_IMG}" --name "${KIND_CLUSTER_NAME}"
    kind load docker-image "${WORKER_IMG}" --name "${KIND_CLUSTER_NAME}"
}

deploy_charts(){
    log_info "Deploying Helm charts (API & Worker) to namespace ${K8S_NAMESPACE}..."
    helm upgrade --install api ./ops/helm/api -n dev \
    --set image.repository="$(cut -d: -f1 <<< "${API_IMG}")" \
        --set image.tag="$(cut -d: -f2 <<< "${API_IMG}")" \
        --set service.port=80 \
        --set containerPort=8000

    helm upgrade --install worker ./ops/helm/worker -n dev \
        --set image.repository="$(cut -d: -f1 <<< "${WORKER_IMG}")" \
        --set image.tag="$(cut -d: -f2 <<< "${WORKER_IMG}")"

    log_info "Waiting for deployments to be ready..."
    kubectl -n "${K8S_NAMESPACE}" rollout status deploy/api --timeout=240s || true
    kubectl -n "${K8S_NAMESPACE}" rollout status deploy/worker --timeout=240s || true

    log_info "Forwarding API service to localhost:8000..."
    kubectl -n "${K8S_NAMESPACE}" port-forward svc/api 8000:80 > /tmp/pf.log 2>&1 &
}

smoke_test(){
    log_info "Running helm smoke test..."
    helm test api -n dev
    log_info "Helm test completed."
    log_info "You can access the API at http://localhost:8000"
    log_info "Check port-forward logs at /tmp/pf.log"
    # remove helm test pods
    kubectl delete pods -l helm.sh/hook=test
}

main(){
    # shellcheck disable=SC1091
    source "${WORKSPACE}/ops/scripts/libs/common.sh"
    build_images
    load_images_into_kind
    deploy_charts
    smoke_test
}

############# MAIN #############
main
