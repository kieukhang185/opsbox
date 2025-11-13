#!/usr/bin/env bash
# Teardown script for OpsBox local development environment
# This script deletes the Kubernetes namespaces and optionally the kind cluster.
# Usage: ./teardown.sh [--delete-cluster]
# Options:
#   --delete-cluster    Also delete the kind cluster (default: false)
# Examples:
#   ./teardown.sh                 # Deletes namespaces only
#   ./teardown.sh --delete-cluster # Deletes namespaces and the kind cluster
# Note:
# - Ensure you have the necessary permissions to delete the resources.
# - This script assumes you have `kind`, `kubectl`, and `helm` installed and configured.

set -euo pipefail

# shellcheck disable=SC2155
export WORKSPACE="$(pwd)"

KIND_CLUSTER_NAME="${KIND_CLUSTER_NAME:-opsbox}"
K8S_NAMESPACE="${K8S_NAMESPACE:-dev}"
MONITORING_NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"
ARGOCD_NAMESPACE="${ARGOCD_NAMESPACE:-argocd}"
ARGO_ROLLOUT_NAMESPACE="${ARGO_ROLLOUT_NAMESPACE:-argo-rollouts}"

# shellcheck disable=SC1091
source "${WORKSPACE}/ops/scripts/libs/common.sh"
pushd "${WORKSPACE}" || exit 1


delete_ns_object(){
    local objects="api worker pg rabbitmq redis"
    for obj in $objects; do
        log_warn "Deleted ${obj} helm release"
        helm uninstall "${obj}" -n "${K8S_NAMESPACE}" || true
    done
    kubectl -n "${K8S_NAMESPACE}" delete secret opxsbox-secret --ignore-not-found
    kubectl -n "${K8S_NAMESPACE}" delete job opsbox-smoke --ignore-not-found

    kubectl delete ns "${K8S_NAMESPACE}" --ignore-not-found
    kubectl delete ns "${MONITORING_NAMESPACE}" --ignore-not-found
    kubectl delete ns "${ARGOCD_NAMESPACE}" --ignore-not-found
    kubectl delete ns "${ARGO_ROLLOUT_NAMESPACE}" --ignore-not-found
}


delete_kind_cluster(){
    if ! need "kind"; then
        log_error "Kind is not installed, please install it first..."
        exit 1
    fi
    if kind get clusters | grep -q "^${KIND_CLUSTER_NAME}$"; then
        log_warn "Deleting kind cluster ${KIND_CLUSTER_NAME}..."
        kind delete cluster --name "${KIND_CLUSTER_NAME}"
        log_warn "Kind cluster ${KIND_CLUSTER_NAME} deleted..."
    else
        log_warn "Kind cluster ${KIND_CLUSTER_NAME} does not exist..."
    fi
}


main (){
    local tools="kind kubectl helm"
    for tool in $tools; do need "$tool"; done

    local delete_cluster=false
    while [[ $# -gt 0 ]]; do
        case $1 in
            -cluster|--delete-cluster)
                delete_cluster=true
                shift ;;
            -h|--help)
                log_info "Usage: $0 [--delete-cluster]"
                exit 0;;
            *)
                log_warn "Unknown option: $1"
                log_info "Usage: $0 [--delete-cluster]"
                exit 1;;
        esac
    done

    delete_ns_object
    if [[ "${delete_cluster}" = true ]]; then
        delete_kind_cluster
    else
        log_warn "Skipping kind cluster deletion. Use --delete-cluster to delete the cluster."
    fi
    log_info "Teardown completed."
}


# Execute the main function
main "$@"
