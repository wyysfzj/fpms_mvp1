#!/usr/bin/env bash
set -euo pipefail

echo "== Release Gate =="

FOUND=0
FAIL=0

shopt -s nullglob
for d in artifacts/ENH-*; do
  if [[ -d "$d" ]]; then
    FOUND=1
    TASK_ID="$(basename "$d")"
    echo "-- validating ${TASK_ID}"
    if ! ./scripts/task_validate.sh "${TASK_ID}"; then
      FAIL=1
    fi
  fi
done
shopt -u nullglob

if [[ $FOUND -eq 0 ]]; then
  echo "WARN: no artifacts/ENH-* directories found. Nothing to validate."
  exit 0
fi

if [[ $FAIL -ne 0 ]]; then
  echo "== RELEASE GATE: FAIL =="
  exit 1
fi

echo "== RELEASE GATE: PASS =="
