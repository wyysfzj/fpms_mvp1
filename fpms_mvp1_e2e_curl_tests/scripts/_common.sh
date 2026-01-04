#!/usr/bin/env bash
set -euo pipefail

: "${BASE_URL:=http://localhost:8000}"
: "${API_PREFIX:=/api/v1}"
: "${FPMS_TOKEN:?FPMS_TOKEN must be set}"

AUTH_HEADER="Authorization: Bearer ${FPMS_TOKEN}"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }
}

api() {
  local method="$1"; shift
  local path="$1"; shift
  local data_file="${1:-}"
  local url="${BASE_URL}${API_PREFIX}${path}"

  if [[ -n "${data_file}" ]]; then
    curl -sS -i -X "${method}" "${url}"       -H "${AUTH_HEADER}"       -H "Content-Type: application/json"       --data @"${data_file}"
  else
    curl -sS -i -X "${method}" "${url}"       -H "${AUTH_HEADER}"
  fi
}

body() { sed -n '/^{/,$p'; }

status_code() { head -n 1 | awk '{print $2}'; }

assert_status() {
  local expected="$1"; local actual="$2"
  if [[ "${actual}" != "${expected}" ]]; then
    echo "Expected HTTP ${expected}, got ${actual}" >&2
    return 1
  fi
}

save_state_kv() { echo "export ${1}="${2}"" >> run_state.env; }
