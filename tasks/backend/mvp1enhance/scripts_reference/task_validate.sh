#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
if [[ -z "$TASK_ID" ]]; then
  echo "Usage: scripts/task_validate.sh <TASK-ID>"
  exit 2
fi

ART_DIR="artifacts/${TASK_ID}"
FAIL=0

req_file() {
  local f="$1"
  if [[ ! -f "$f" ]]; then
    echo "FAIL: missing file: $f"
    FAIL=1
  else
    echo "OK:   $f"
  fi
}

req_dir() {
  local d="$1"
  if [[ ! -d "$d" ]]; then
    echo "FAIL: missing dir: $d"
    FAIL=1
  else
    echo "OK:   $d/"
  fi
}

echo "== Task Gate Validate: ${TASK_ID} =="

req_dir "${ART_DIR}"
req_dir "${ART_DIR}/outputs"
req_dir "${ART_DIR}/git"
req_file "${ART_DIR}/summary.md"
req_file "${ART_DIR}/git/diff.patch"
req_file "${ART_DIR}/results.jsonl"

if [[ -f "${ART_DIR}/results.jsonl" ]]; then
  if grep -Eq '"step":"lint".*"rc":0' "${ART_DIR}/results.jsonl"; then
    echo "OK:   lint rc=0 recorded"
  else
    echo "FAIL: lint step not found or not rc=0"
    FAIL=1
  fi

  if grep -Eq '"step":"test".*"rc":0' "${ART_DIR}/results.jsonl"; then
    echo "OK:   test rc=0 recorded"
  else
    echo "FAIL: test step not found or not rc=0"
    FAIL=1
  fi

  if grep -Eq '"step":"e2e".*"rc":0' "${ART_DIR}/results.jsonl"; then
    echo "OK:   e2e rc=0 recorded"
  else
    echo "INFO: e2e not recorded (may be N/A)"
  fi
fi

if [[ $FAIL -ne 0 ]]; then
  echo "== RESULT: FAIL =="
  exit 1
fi

echo "== RESULT: PASS =="
