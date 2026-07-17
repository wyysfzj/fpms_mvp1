#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: ./scripts/evidence_finalize.sh <TASK-ID>"
  exit 2
fi

TASK_ID=$1
ART_DIR="artifacts/$TASK_ID"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

python3 "$SCRIPT_DIR/evidence_scope.py" finalize "$TASK_ID"

SUMMARY_PATH="$ART_DIR/summary.md"
if [ ! -f "$SUMMARY_PATH" ]; then
  cat <<'SUMMARY' >"$SUMMARY_PATH"
# Summary

## Commands
- 

## Results
- 

## Notes
- 
SUMMARY
fi
