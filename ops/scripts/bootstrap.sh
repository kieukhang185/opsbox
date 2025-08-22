#!/usr/bin/env bash
set -Eeuo pipefail

setup_tool(){
  source setup.sh
  install_"$1"
}

need() { command -v "$1" >/dev/null || { echo "Missing: $1"; setup_tool $1; }; }
for bin in docker kind kubectl helm; do need "$bin"; done

CLUSTER=opsbox
if ! kind get clusters | grep -q "^${CLUSTER}$"; then
  kind create cluster --name "$CLUSTER"
fi

# Postgres & Redis (bitnami)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm upgrade --install pg bitnami/postgresql --set auth.postgresPassword=postgres --namespace dev --create-namespace
helm upgrade --install redis bitnami/redis --set architecture=standalone --namespace dev

# Build images and load into kind
docker build -t opsbox-api:dev api
docker build -t opsbox-worker:dev worker
kind load docker-image opsbox-api:dev --name "$CLUSTER"
kind load docker-image opsbox-worker:dev --name "$CLUSTER"

# Install API
helm upgrade --install api ./ops/helm/api -n dev \
  --set image.repository=opsbox-api --set image.tag=dev \
  --set service.port=80 \
  --set containerPort=8000

# Install Worker (as a Deployment)
helm upgrade --install worker ./ops/helm/worker -n dev \
  --set image.repository=opsbox-worker --set image.tag=dev

# Smoke: port-forward API and hit /health
kubectl -n dev rollout status deploy/api
kubectl -n dev port-forward svc/api 8080:80 >/tmp/pf.log 2>&1 &
sleep 2
# shellcheck disable=SC2015
curl -sf http://127.0.0.1:8080/health | grep -q '"ok"' && echo "SMOKE: OK" || (echo "SMOKE: FAIL"; exit 1)
