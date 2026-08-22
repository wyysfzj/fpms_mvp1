#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: ./scripts/task_validate.sh <TASK-ID>"
  exit 2
fi

TASK_ID=$1
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

exec python3 "$SCRIPT_DIR/evidence_validate.py" "$TASK_ID" \
  --acceptance-mode task \
  --required-step lint \
  --required-step test
