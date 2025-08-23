#!/bin/bash/env bash

set -euo pipefail

DRY_RUN=1
DEEP_CLEAN=0

log() { printf "\033[1;36m==> %s\033[0m\n" "$*"; }
info() { printf "   -%s\n" "$*"; }

run(){
    if [ "${DRY_RUN}" -eq 1 ]; then
        info "Dry run: $*"
    else
        log "Running: $*"
        "$@"
    fi
}

exists(){ command -v "$1" >/dev/null 2>&1; }

usage(){
    cat <<"USAGE"
Usage: cleanup.sh [OPTIONS]

Options:
  -do, --do-it       Execute changes (default is dry-run preview)
  -d, --deep-clean   Perform a deep clean (removes all unused Docker images and containers)
  -h, --help         Show this help message and exit
USAGE
}

for arg in "$@"; do
    case "${arg}" in
        -do|--do-it)
            DRY_RUN=0
            ;;
        -d|--deep-clean)
            DEEP_CLEAN=1
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log "Unknown option: ${arg}"
            usage
            exit 1
            ;;
    esac
done

before() { log "Disk usage BEFORE: "; df -h / | tail -1; }
after() { log "Disk usage AFTER: "; df -h / | tail -1; }

cleanup_journal(){
    if exists journalctl; then
        log "System logs (journalctl)"
        run "journalctl --disk-usage"
        run "journalctl --vacuum-time=1d"
    fi
}

cleanup_apt(){
    if exists apt-get; then
        log "APT cache and unused packages"
        run "sudo apt-get clean"
        run "sudo apt-get autoremove --purge -y"
    fi
}

cleanup_docker(){
    if exists docker; then
        log "Docker images/containers/networks/build cache"
        run "docker system df"
        run "docker system prune -af"
        if [ "${DEEP_CLEAN}" -eq 1 ]; then
            log "Docker VOLUME (DEEP_CLEAN)"
            run "docker volume prune -f"
            run "docker network prune -f"
            run "docker builder prune -f"
        fi
    fi
}

cleanup_containerd(){
    if exists nerdct1; then
        log "Containerd images/containers/networks/build cache"
        run "nerdctl system df || true"
        run "nerdctl system prune -af || true"
        if [ "${DEEP_CLEAN}" -eq 1 ]; then
            log "Containerd VOLUME (DEEP_CLEAN)"
            run "nerdctl volume prune -f || true"
        fi
    fi
}

cleanup_kind(){
    if exists kind; then
        if [[ ${DEEP_CLEAN} -eq 1 ]]; then
            log "Kind VOLUME (DEEP_CLEAN)"
            cluster=$(kind get clusters 2>/dev/null || true)
            if [[ -n "${cluster}" ]]; then
                while read -r c; do
                    [[ -z $c ]] && continue
                    info "Deleting kind cluster $c"
                    run "kind delete cluster --name \$c\""
                done <<< "${cluster}"
            else
                info "No kind clusters found"
            fi
        else
            log "Kind clusters (preview-only); use --deep-clean to remove"
            run "kind get clusters || true"
        fi
    fi
}

cleanup_minikube(){
    if exists minikube; then
        if [[ "${DEEP_CLEAN}" -eq 1 ]]; then
            log "Minikube VOLUME (DEEP_CLEAN)"
            run "minikube delete --all --purge || true"
        else
            log "minikube clusters (preview-only); use --deep-clean to remove"
            run "minikube status --all || true"
        fi
    fi
}

cleanup_kubectl(){
    if exists kubectl; then
        log "kubectl client cache"
        run "rm -rf ~/.kube/http-cache"
        run "rm -rf ~/.kube/cache"
        if [[ "${DEEP_CLEAN}" -eq 1 ]]; then
            log "Kubectl VOLUME (DEEP_CLEAN)"
            run "kubectl delete --all --force --grace-period=0 || true"
        else
            log "kubectl resources (preview-only); use --deep-clean to remove"
            run "kubectl get all || true"
        fi
    fi
}

cleanup_helm(){
    if exists helm; then
        log "Helm releases"
        run "helm list --all-namespaces"

        log "Helm cache"
        run "rm -rf ~/.cache/helm"
        run "rm -rf ~/.config/helm/repositories.yaml.lock || true"
        if [[ "${DEEP_CLEAN}" -eq 1 ]]; then
            log "Helm VOLUME (DEEP_CLEAN)"
            run "helm uninstall --all-namespaces || true"

            log "Helm plugins & repo cache (AGGRESSIVE)"
            run "rm -rf ~/.local/share/helm/plugins"
            run "helm repo remove $(helm repo list -o yaml 2>/dev/null | awk '/name:/{print $2}' | xargs 2>/dev/null) || true"
            run "rm -rf ~/.cache/helm/repository"
        else
            log "Helm releases (preview-only); use --deep-clean to remove"
            run "helm list --all-namespaces || true"
        fi
    fi
}

cleanup_python(){
    log "Python caches"
    run "rm -rf ~/.cache/pip"
    run "rm -rf ~/.local/share/virtualenvs"
    run "rm -rf ~/.cache/pip-tools ~/.cache/wheel || true"
    if [[ -d ~/.pyenv ]] ; then
        log "Pyenv environments"
        run "rm -rf ~/.pyenv/versions/*"
    fi
    if [[ "${DEEP_CLEAN}" -eq 1 ]]; then
        log "__pycache__ (AGGRESSIVE, current repo)"
        run "find . -type d -name '__pycache__' -prune -exec rm -rf {} +"
        run "rm -rf ~/.cache/pypoetry || true"
    else
        log "Pyenv environments (preview-only); use --deep-clean to remove"
        run "pyenv versions || true"
    fi
}

cleanup_snaps(){
    if exists snap; then
        log "Snap packages and cache"
        run "snap list --all | awk '/disabled/{print \$1, \$3}' | while read n r; do sudo snap remove \"\$n\" --revision=\"\$r\"; done"
        if [[ "${DEEP_CLEAN}" -eq 1 ]]; then
            log "Snap VOLUME (DEEP_CLEAN)"
            run "sudo snap set system refresh.retain=2 || true"
        else
            log "Snap packages (preview-only); use --deep-clean to remove"
        fi
    fi
}

cleanup_logs_misc() {
  log "Rotated logs under /var/log"
  run "sudo rm -f /var/log/*.gz /var/log/*.[0-9] /var/log/*-???????"
}

summary_big_files() {
  log "Top disk consumers (preview)"
  run "sudo du -hx / | sort -rh | head -n 20"
  if exists docker; then
    run "docker system df"
  fi
}

main() {
  before
  summary_big_files
  cleanup_journal
  cleanup_apt
  cleanup_docker
  cleanup_containerd
  cleanup_kind
  cleanup_k3d
  cleanup_minikube
  cleanup_kubectl
  cleanup_helm
  cleanup_python
  cleanup_snaps
  cleanup_logs_misc
  after
  if (( "${DRY_RUN}" )); then
    echo
    echo "Dry-run complete. Re-run with --do-it to apply changes."
  fi
}

main "$@"