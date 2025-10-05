#!/usr/bin/env bash

# Config
: "${LOG_LEVEL:=info}"        # debug|info|warn|error
: "${LOG_JSON:=0}"            # 1 to emit JSON lines
: "${LOG_NAME:=${0##*/}}"     # script name

# level -> numeric
_log_num(){
    case "${LOG_LEVEL}" in
        debug)  echo 10;;
        info)   echo 20;;
        warn)   echo 30;;
        error)  echo 40;;
        *)      echo 20;;
    esac
}

LOG_LEVEL_NUM="$(_log_num "${LOG_LEVEL}")"

_ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

# Color
if [[ -t 2 && "${LOG_JSON}" != "1" ]]; then
    C_GRAY=$'\e[90m'
    C_GREEN=$'\e[32m'
    C_YELLOW=$'\e[33m'
    C_RED=$'\e[31m'
    C_CYAN=$'\e[36m'
    C_RESET=$'\e[0m'
else
    C_GRAY=""
    C_GREEN=""
    C_YELLOW=""
    C_RED=""
    C_CYAN=""
    C_RESET=""
fi

_log(){
    local level="$1"; shift
    local msg="$*"
    # shellcheck disable=SC2155
    local level_num="$(_log_num "${level}")"
    (( level_num < LOG_LEVEL_NUM )) && return

    if [[ "${LOG_JSON}" == "1" ]]; then
        # JSON line (safe-ish escaping)
        printf '{"ts":"%s","level":"%s","name":"%s","pid":%d,"msg":%s}\n' \
        "$(_ts)" "[${level}]" "${LOG_NAME}" "$$" "$(printf '%s' "${msg}" \
        | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')" >&2
    else
        local color="${C_CYAN}"
        [[ "${level}" == "info" ]] && color="${C_GREEN}"
        [[ "${level}" == "warn" ]] && color="${C_YELLOW}"
        [[ "${level}" == "error" ]] && color="${C_RED}"
        printf "%s[%s] %s%-5s%s %s\n" "${C_GRAY}" "$(_ts)" "${color}" "[${level^^}] " "${msg}" "${C_RESET}" >&2
    fi
}

log_debug() { _log debug "$*"; }
log_info()  { _log info  "$*"; }
log_warn()  { _log warn  "$*"; }
log_error() { _log error "$*"; }

enable_xtrace() {
  [[ "${LOG_LEVEL}" == "debug" ]] || return 0
  export PS4='+ $(date -u +"%H:%M:%S") ${BASH_SOURCE##*/}:${LINENO} ${FUNCNAME[0]:-main}() '
  set -x
}
