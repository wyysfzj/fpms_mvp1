#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: ./scripts/evidence_run.sh <TASK-ID> <step> <command...>"
  exit 2
fi

TASK_ID=$1
STEP=$2
shift 2

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$SCRIPT_DIR/taskctl" "$TASK_ID" record "$STEP" -- "$@"
