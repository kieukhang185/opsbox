#!/usr/bin/env bash
set -Eeuo pipefail

create_kind_cluster(){
    local kind_cluster_name=$1

    if kind get clusters | grep -q "^${kind_cluster_name}$"; then
        log_info "Kind cluster ${kind_cluster_name} already exists..."
        return 0
    fi
    log_info "Creating kind cluster ${kind_cluster_name}..."
    kind create cluster --name "${kind_cluster_name}" --config "${WORKSPACE}/ops/scripts/templates/kind-${kind_cluster_name}.yaml"
    log_info "Kind cluster ${kind_cluster_name} created..."
}

ensure_namespace(){
    local namespace=$1

    log_info "Ensuring namespace ${namespace}"
    kubectl get namespace "${namespace}" || kubectl create namespace "${namespace}" --dry-run=client -o yaml | kubectl apply -f -

}

helm_repos(){
    local helm_repo_name=$1
    local helm_repo_url=$2

    log_info "Adding helm repos..."
    helm repo add "${helm_repo_name}" "${helm_repo_url}" >/dev/null 2>&1 || true
    helm repo update
}

helm_install(){
    local release_name=$1
    local chart_path=$2
    local namespace=$3
    local value_file=$4

    if [[ "${release_name}" == "" ]]; then
        log_error "Release name cannot be empty. Exiting."
        exit 1
    fi

    if [[ "${chart_path}" == "" ]]; then
        log_error "Chart path cannot be empty. Exiting."
        exit 1
    fi

    if [[ "${namespace}" == "" ]]; then
        log_error "Namespace cannot be empty. Exiting."
        exit 1
    fi

    if [ "${value_file}" == "" ]; then
        value_file="-"
    elif [ ! -f "${value_file}" ]; then
        log_error "Value file ${value_file} does not exist. Exiting."
        exit 1
    fi
    log_info "Installing helm chart ${chart_path} as release ${release_name}..."
    helm upgrade --install "${release_name}" "${chart_path}" --namespace "${namespace}" -f "${value_file}"
}
