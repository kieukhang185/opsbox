#!/usr/bin/env bash
set -Eeuo pipefail

# shellcheck disable=SC2155
export WORKSPACE="$(pwd)"

KIND_CLUSTER_NAME="${KIND_CLUSTER_NAME:-opsbox}"
K8S_NAMESPACE="${K8S_NAMESPACE:-dev}"
MONITORING_NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"
API_IMG="${API_IMG:-opsbox-api:dev}"
WORKER_IMG="${WORKER_IMG:-opsbox-worker:dev}"
BITNAMI_REPO="https://charts.bitnami.com/bitnami"
PROM_REPO="https://prometheus-community.github.io/helm-charts"
MONITORING_ENABLED=false
DEPLOY_ENV="local"
ARGOCD_ENABLED="false"

# shellcheck disable=SC1091
source "${WORKSPACE}/ops/scripts/libs/common.sh"
pushd "$WORKSPACE" || exit 1

while [[ $# -gt 0 ]]; do
    case $1 in
        -env|--environment)
            DEPLOY_ENV="$2"
            shift 2 ;;
        -m|--monitoring)
            MONITORING_ENABLED=true
            shift ;;
        -argocd|--argocd)
            ARGOCD_ENABLED="true"
            shift ;;
        -h|--help)
            log_info "Usage: $0 [--monitoring] [--argocd]"
            exit 0;;
        *)
            log_warn "Unknown option: $1"
            log_info "Usage: $0 [--monitoring]"
            exit 1;;
    esac
done

setup(){
  list_bins=$@
  for bin in $list_bins; do need_install "$bin"; done
}

# shellcheck disable=SC1091
source "${WORKSPACE}/ops/scripts/kubernetes_setup.sh"

create_kind_cluster "${KIND_CLUSTER_NAME}"

ensure_namespace "${K8S_NAMESPACE}"

apply_app_secret(){
    log_info "Applying application secrets..."
    export SOPS_AGE_KEY_FILE="${SOPS_AGE_KEY_FILE:-${WORKSPACE}/ops/infra/age.key}"
    export SOPS_CONFIG="${SOPS_CONFIG:-${WORKSPACE}/.sops.yaml}"
    export ENCRYPTED_SECRETS_FILE="${ENCRYPTED_SECRETS_FILE:-${WORKSPACE}/ops/secrets/dev.app.enc.yaml}"

    exist "${SOPS_AGE_KEY_FILE}" || { log_error "Please create AGE private key at ${SOPS_AGE_KEY_FILE}"; exit 1; }
    exist "${ENCRYPTED_SECRETS_FILE}" || { log_error "Please create encrypted secrets file at ${ENCRYPTED_SECRETS_FILE}"; exit 1; }
    exist "${SOPS_CONFIG}" || { log_error "Please create sops config file at ${SOPS_CONFIG}"; exit 1; }

    sops -d ops/secrets/dev.app.enc.yaml | kubectl -n "${K8S_NAMESPACE}" apply -f -
}

install_deps(){
    if [[ "${MONITORING_ENABLED}" == "true" ]]; then
        ensure_namespace "$MONITORING_NAMESPACE"
        helm_repos "prometheus-community" "$PROM_REPO"
        install_monitoring
    fi

    log_info "Installing Postgres and RabbitMQ..."
    helm upgrade --install pg bitnami/postgresql -n dev -f ops/helm/postgres/values.dev.yaml
    helm upgrade --install rabbitmq bitnami/rabbitmq -n dev -f ops/helm/rabbitmq/values.dev.yaml
    kubectl -n "$K8S_NAMESPACE" rollout status statefulset/pg-postgresql --timeout=240s
}

apply_sa_dev(){
  log_info "Applying service account..."
  kubectl -n "${K8S_NAMESPACE}" apply -f "${WORKSPACE}/ops/scripts/templates/rbac-readonly.yaml"
}

argo_rollouts(){
    kubectl get namespace argo-rollouts >/dev/null 2>&1 || kubectl create namespace argo-rollouts --dry-run=client -o yaml | kubectl apply -f -
    log_info "Ensuring Argo Rollouts is installed..."
    if ! kubectl -n argo-rollouts get deploy argo-rollouts-controller >/dev/null 2>&1; then
        log_info "Installing Argo Rollouts..."
        kubectl create ns argo-rollouts --dry-run=client -o yaml | kubectl apply -f -
        kubectl -n argo-rollouts apply -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
    else
        log_info "Argo Rollouts already installed..."
        return 0
    fi
}

apply_app_secret
install_deps
apply_sa_dev
argo_rollouts

if [[ "${ARGOCD_ENABLED}" == "false" && "${DEPLOY_ENV}" == "local" ]]; then
    log_info "Deploying Helm charts locally..."
    setup docker kind kubectl helm sops age
    bash "${WORKSPACE}/ops/scripts/deploy_helm_local.sh" \
        --api-image "${API_IMG}" \
        --k8s-namespace "${K8S_NAMESPACE}" \
        --kind-cluster-name "${KIND_CLUSTER_NAME}" \
        --monitoring "${MONITORING_ENABLED}" \
        --worker-image "${WORKER_IMG}"
else
    log_info "ArgoCD deployment enabled..."
    setup kind kubectl helm argocd
    bash "${WORKSPACE}/ops/scripts/deploy_argocd.sh"
fi
