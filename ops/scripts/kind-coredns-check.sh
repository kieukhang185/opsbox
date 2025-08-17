#!/usr/bin/env bash
# Recreate a kind cluster, wait for CoreDNS, verify endpoints, fetch metrics, and test DNS.
# Usage: ./kind-coredns-check.sh [cluster-name]
set -euo pipefail

CLUSTER="${1:-opsbox}"
CTX="kind-${CLUSTER}"

need() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: '$1' is required"; exit 1; }; }
need kind
need kubectl
need curl

echo ">>> [1/7] (Re)creating kind cluster: ${CLUSTER}"
if kind get clusters | grep -Fxq "${CLUSTER}"; then
  echo "Cluster '${CLUSTER}' exists. Deleting it for a clean run..."
  kind delete cluster --name "${CLUSTER}" || true
fi
kind create cluster --name "${CLUSTER}"

echo ">>> Setting kube context: ${CTX}"
kubectl config use-context "${CTX}" >/dev/null

echo ">>> [2/7] Waiting for nodes to be Ready..."
kubectl wait --for=condition=Ready node --all --timeout=180s

echo ">>> [3/7] Waiting for CoreDNS deployment to be Available..."
# CoreDNS deployment name is 'coredns' in kube-system on standard kind clusters
kubectl -n kube-system rollout status deploy/coredns --timeout=180s

echo ">>> [4/7] Verifying kube-dns Service and Endpoints..."
kubectl -n kube-system get svc kube-dns -o wide
# Wait for at least 1 endpoint address
ATTEMPTS=0
until [[ -n "$(kubectl -n kube-system get endpoints kube-dns -o jsonpath='{.subsets[*].addresses[*].ip}')" ]]; do
  ATTEMPTS=$((ATTEMPTS+1))
  if [[ $ATTEMPTS -gt 30 ]]; then
    echo "ERROR: kube-dns has no ready endpoints after ~30s"
    kubectl -n kube-system get endpoints kube-dns -o yaml || true
    exit 1
  fi
  sleep 1
done
kubectl -n kube-system get endpoints kube-dns -o wide

DNS_IP="$(kubectl -n kube-system get svc kube-dns -o jsonpath='{.spec.clusterIP}')"
echo ">>> kube-dns ClusterIP: ${DNS_IP}"

echo ">>> [5/7] Fetching CoreDNS metrics (HTTP 9153)..."
METRICS_OK=0
# Try API server service proxy first (if the port is named 'metrics')
if kubectl -n kube-system get --raw "/api/v1/namespaces/kube-system/services/kube-dns:metrics/proxy/metrics" \
  | head -n 12; then
  METRICS_OK=1
else
  echo "API proxy to :metrics failed; trying port-forward..."
fi

if [[ $METRICS_OK -eq 0 ]]; then
  # Fallback: port-forward and curl metrics
  PF_LOG="$(mktemp)"; PF_PID=""
  # shellcheck disable=SC2015
  cleanup_pf() { [[ -n "${PF_PID}" ]] && kill "${PF_PID}" 2>/dev/null || true; rm -f "${PF_LOG}" 2>/dev/null || true; }
  trap cleanup_pf EXIT

  kubectl -n kube-system port-forward svc/kube-dns 9153:9153 >"${PF_LOG}" 2>&1 &
  PF_PID=$!
  # Wait briefly for port-forward to bind
  for _ in {1..20}; do
    if ss -lnt 2>/dev/null | grep -q ":9153 "; then break; fi
    sleep 0.2
  done
  echo "---- /metrics (via port-forward) ----"
  curl -fsS http://127.0.0.1:9153/metrics | head -n 12 || {
    echo "WARN: Could not fetch metrics via port-forward."
  }
fi

echo ">>> [6/7] Launching a toolbox pod to test DNS resolution..."
# Create a long-lived pod, wait Ready, exec dig, then delete
kubectl run dns-test --image=ghcr.io/nicolaka/netshoot:latest --restart=Never -- sleep 3600
kubectl wait --for=condition=Ready pod/dns-test --timeout=90s
echo "---- dig kubernetes.default.svc.cluster.local @${DNS_IP} ----"
kubectl exec dns-test -- dig +short kubernetes.default.svc.cluster.local @"${DNS_IP}" || true
echo "Cleaning up test pod..."
kubectl delete pod dns-test --wait=false >/dev/null

echo ">>> [7/7] Summary"
echo "Cluster: ${CLUSTER} (context ${CTX})"
echo "CoreDNS: Ready, kube-dns endpoints present"
echo "Metrics: Shown above (via API proxy or port-forward)"
echo "DNS test: See dig output above"
echo "All done ✅"
