#!/usr/bin/env bash

# Deploy ArgoCD and sync applications
# within a kind Kubernetes cluster.
# Usage: deploy_argocd.sh \
#   --env <environment> \
#   --k8s-namespace <namespace> \
#   --kind-cluster-name <cluster_name> [--monitoring]


# while [[ $# -gt 0 ]]; do
#     case $1 in
#         -k|--k8s-namespace)
#             k8s_namespace="$2"
#             shift 2 ;;
#         -c|--kind-cluster-name)
#             kind_cluster_name="$2"
#             shift 2 ;;
#         -m|--monitoring)
#             monitoring_enabled="$2"
#             shift ;;
#         *)
#             log_warn "Unknown option: $1"
#             exit 1;;
#     esac
# done

source "${WORKSPACE}/ops/scripts/libs/common.sh"
source "${WORKSPACE}/ops/scripts/kubernetes_setup.sh"

ARGO_HELM_REPO="https://argoproj.github.io/argo-helm"
ARGOCD_NAMESPACE="argocd"

ensure_namespace "${ARGOCD_NAMESPACE}"
helm_repos "argo" "${ARGO_HELM_REPO}"
helm_install "$ARGOCD_NAMESPACE"  "argo/argo-cd" "${ARGOCD_NAMESPACE}" "gitops/argocd.values.yaml"
kubectl -n "${ARGOCD_NAMESPACE}" rollout status deploy/argocd-server
kubectl -n "${ARGOCD_NAMESPACE}" port-forward svc/argocd-server 8083:80 > /dev/null 2>&1 &
echo "Argo CD UI/API at http://localhost:8080"

kubectl apply -n argocd -f gitops/apps/project-opsbox.yaml
kubectl apply -n argocd -f gitops/application.yaml
