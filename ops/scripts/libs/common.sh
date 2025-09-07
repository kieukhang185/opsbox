#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIBS_DIR="${SCRIPT_DIR}/../libs"

# shellcheck disable=SC1091
source "${LIBS_DIR}/log.sh"

# Check if a command exists
need() { command -v "$1" >/dev/null || { echo "Missing: $1"; exit 1; } ; }

setup_tool(){
  # shellcheck disable=SC1091
  source "${WORKSPACE}/ops/scripts/setup.sh"
  install_"$1"
}

# Check and install a command if not exists
need_install() { command -v "$1" >/dev/null || { echo "Missing: $1"; setup_tool "$1"; }; }

# Check if a file or directory exists
exist(){
  if [[ -e $1 ]]; then
    log_info "$1 existed..."
    return 0
  else
    log_error "$1 does not exist, please check..."
    return 1
  fi
}

# Check if a docker image exists
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
