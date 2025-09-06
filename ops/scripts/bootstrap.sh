#!/usr/bin/env bash
set -Eeuo pipefail

# shellcheck disable=SC2155
export WORKSPACE="$(find "${HOME}" -type d -name opsbox)"
pushd "$WORKSPACE" || exit 1

setup_tool(){
  # shellcheck disable=SC1091
  source "${WORKSPACE}/ops/scripts/setup.sh"
  install_"$1"
}

exist_file(){
  if [[ -f $1 ]]; then
    echo "File $1 existed..."
    return 0
  else
    echo "File $1 does not exist, please check..."
    return 1
  fi
}

exist_image(){
  # shellcheck disable=SC2086
  if [[ -n "$(docker images -q $1 2> /dev/null)" ]]; then
    echo "Image $1 existed..."
    return 0
  else
    echo "Image $1 does not exist, start building..."
    return 1
  fi
}

need() { command -v "$1" >/dev/null || { echo "Missing: $1"; setup_tool "$1"; }; }
for bin in docker kind kubectl helm sops; do need "$bin"; done

CLUSTER=opsbox
if ! kind get clusters | grep -q "^${CLUSTER}$"; then
  kind create cluster --name "$CLUSTER"
fi

# Create monitor namespace for prometheus and grafana
kubectl create ns monitoring --dry-run=client -o yaml | kubectl apply -f -
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --set grafana.enabled=true \
  --set grafana.service.type=ClusterIP \
  --set prometheus.prometheusSpec.scrapeInterval="15s"

# Postgres (bitnami)
kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -
helm repo add bitnami https://charts.bitnami.com/bitnami
helm upgrade --install pg bitnami/postgresql -n dev -f ops/helm/postgres/values.dev.yaml
helm upgrade --install rabbitmq bitnami/rabbitmq -n dev -f ops/helm/rabbitmq/values.dev.yaml

# Build images and load into kind
exist_image "opsbox-api:dev" || docker build -f api/Dockerfile -t opsbox-api:dev .
exist_image "opsbox-worker:dev" || docker build -f worker/Dockerfile -t opsbox-worker:dev .
kind load docker-image opsbox-api:dev --name "$CLUSTER"
kind load docker-image opsbox-worker:dev --name "$CLUSTER"

# Install API
export SOPS_AGE_KEY_FILE="${WORKSPACE}/ops/infra/age.key"
export SOPS_CONFIG="${WORKSPACE}/.sops.yaml"
exist_file "$SOPS_AGE_KEY_FILE" || { echo "Please create age key file at ${SOPS_AGE_KEY_FILE}"; exit 1; }
exist_file "$SOPS_CONFIG" || { echo "Please create sops config file at ${SOPS_CONFIG}"; exit 1; }
sops -d ops/secrets/dev.app.enc.yaml | kubectl apply -f - -n dev
helm upgrade --install api ./ops/helm/api -n dev \
  --set image.repository=opsbox-api --set image.tag=dev \
  --set service.port=80 \
  --set containerPort=8000

# Install Worker (as a Deployment)
helm upgrade --install worker ./ops/helm/worker -n dev \
  --set image.repository=opsbox-worker --set image.tag=dev

# Smoke: port-forward API and hit /health
kubectl -n dev rollout status statefulset/rabbitmq
kubectl -n dev rollout status deploy/api
kubectl -n dev port-forward svc/api 8080:80 >/tmp/pf.log 2>&1 &

time_sleep=30
retry=3
while [ $retry -gt 0 ]; do
  if curl -sf "http://127.0.0.1:8080/health" | grep -q '"ok"'; then
    echo "SMOKE: OK"
    exit 0
  fi
  echo "Waiting ${time_sleep}s for port-forward to be ready..."
  sleep "${time_sleep}"
  retry=$((retry - 1))
  [[ $retry -eq 0 ]] && eval "echo 'SMOKE: FAIL' && exit 1"
done

popd
