#!/usr/bin/env bash
set -euo pipefail

shopt -s nullglob

ART_DIRS=(artifacts/ENH-*)
if [ "${#ART_DIRS[@]}" -eq 0 ]; then
  echo "No task artifacts found"
  exit 1
fi

PASS=0
FAIL=0

for dir in "${ART_DIRS[@]}"; do
  TASK_ID=${dir#artifacts/}
  if ./scripts/task_validate.sh "$TASK_ID"; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
  fi
done

echo "Release Gate: $PASS passed, $FAIL failed"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
