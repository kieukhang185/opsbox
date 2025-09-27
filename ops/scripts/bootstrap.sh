#!/usr/bin/env bash
set -Eeuo pipefail

# shellcheck disable=SC2155
export WORKSPACE="$(find "${HOME}" -type d -name opsbox)"

KIND_CLUSTER_NAME="${KIND_CLUSTER_NAME:-opsbox}"
K8S_NAMESPACE="${K8S_NAMESPACE:-dev}"
MONITORING_NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"
API_IMG="${API_IMG:-opsbox-api:dev}"
WORKER_IMG="${WORKER_IMG:-opsbox-worker:dev}"
BITNAMI_REPO="https://charts.bitnami.com/bitnami"
PROM_REPO="https://prometheus-community.github.io/helm-charts"
MONITORING_ENABLED=false

# shellcheck disable=SC1091
source "${WORKSPACE}/ops/scripts/libs/common.sh"
pushd "$WORKSPACE" || exit 1

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--monitoring)
            MONITORING_ENABLED=true
            shift ;;
        -h|--help)
            log_info "Usage: $0 [--monitoring]"
            exit 0;;
        *)
            log_warn "Unknown option: $1"
            log_info "Usage: $0 [--monitoring]"
            exit 1;;
    esac
done

setup(){
  list_bins="docker kind kubectl helm sops age"
  for bin in $list_bins; do need_install "$bin"; done
}

create_kind_cluster(){
  if kind get clusters | grep -q "^${KIND_CLUSTER_NAME}$"; then
    log_info "Kind cluster ${KIND_CLUSTER_NAME} already exists..."
    return 0
  fi
  log_info "Creating kind cluster ${KIND_CLUSTER_NAME}..."
  kind create cluster --name "${KIND_CLUSTER_NAME}" --config "${WORKSPACE}/ops/scripts/templates/kind-${KIND_CLUSTER_NAME}.yaml"
  log_info "Kind cluster ${KIND_CLUSTER_NAME} created..."
}

ensure_namespace(){
  log_info "Ensuring namespace ${K8S_NAMESPACE} and ${MONITORING_NAMESPACE}..."
  kubectl get namespace "${K8S_NAMESPACE}" || kubectl create namespace "${K8S_NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -
  kubectl config set-context --current --namespace="${K8S_NAMESPACE}" >/dev/null 2>&1 || true
  if [[ "$MONITORING_ENABLED" = true ]]; then
    kubectl get namespace "${MONITORING_NAMESPACE}" || kubectl create namespace "${MONITORING_NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -
  fi
}

helm_repos(){
  log_info "Adding helm repos..."
  helm repo add bitnami "${BITNAMI_REPO}" >/dev/null 2>&1 || true
  if [[ "$MONITORING_ENABLED" = true ]]; then
    helm repo add prometheus-community "${PROM_REPO}" >/dev/null 2>&1 || true
  fi
  helm repo update
}

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

install_monitoring(){
  log_info "Installing monitoring stack..."
  helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
    --namespace "${MONITORING_NAMESPACE}" \
    --set grafana.enabled=true \
    --set grafana.service.type=ClusterIP \
    --set prometheus.prometheusSpec.scrapeInterval="15s"
}

install_deps(){
  if [[ "$MONITORING_ENABLED" = true ]]; then
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
  # kubectl -n "${K8S_NAMESPACE}" rollout status deploy/worker --timeout=240s || true

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


############# MAIN #############
setup
create_kind_cluster
ensure_namespace
helm_repos
apply_app_secret
install_deps
apply_sa_dev
argo_rollouts
build_images
load_images_into_kind
deploy_charts
smoke_test

popd
