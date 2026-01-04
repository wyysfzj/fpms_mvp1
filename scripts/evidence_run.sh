#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: ./scripts/evidence_run.sh <TASK-ID> <step> <command...>"
  exit 2
fi

TASK_ID=$1
STEP=$2
shift 2

ART_DIR="artifacts/$TASK_ID"
OUT_DIR="$ART_DIR/outputs"
mkdir -p "$OUT_DIR"

TS=$(date +"%Y%m%dT%H%M%S")
LOG_PATH="$OUT_DIR/${TS}_${STEP}.log"

CMD_STR=$(printf '%q ' "$@")
CMD_STR=${CMD_STR% }

printf '{"ts":"%s","step":"%s","cmd":"%s"}\n' \
  "$TS" "$STEP" "$CMD_STR" >> "$ART_DIR/commands.jsonl"

set +e
"$@" >"$LOG_PATH" 2>&1
RC=$?
set -e

printf '{"ts":"%s","step":"%s","rc":%d,"log":"%s"}\n' \
  "$TS" "$STEP" "$RC" "$LOG_PATH" >> "$ART_DIR/results.jsonl"

if [ "$RC" -ne 0 ]; then
  echo "Command failed with rc=$RC. See $LOG_PATH"
  exit "$RC"
fi
