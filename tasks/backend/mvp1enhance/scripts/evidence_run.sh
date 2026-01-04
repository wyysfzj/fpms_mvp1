#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
STEP="${2:-}"
shift 2 || true

if [[ -z "$TASK_ID" || -z "$STEP" ]]; then
  echo "Usage: scripts/evidence_run.sh <TASK-ID> <step> <command...>"
  exit 2
fi

ART_DIR="artifacts/${TASK_ID}"
OUT_DIR="${ART_DIR}/outputs"
mkdir -p "${OUT_DIR}"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="${OUT_DIR}/${TS}_${STEP}.log"
CMD_STR="$*"

# record command
printf '{"ts":"%s","step":"%s","cmd":"%s"}\n' "${TS}" "${STEP}" "${CMD_STR//\"/\\\"}" >> "${ART_DIR}/commands.jsonl"

# execute and capture output
set +e
"$@" >"${OUT_FILE}" 2>&1
RC=$?
set -e

# record result
printf '{"ts":"%s","step":"%s","rc":%s,"out":"%s"}\n' "${TS}" "${STEP}" "${RC}" "${OUT_FILE}" >> "${ART_DIR}/results.jsonl"

if [[ $RC -ne 0 ]]; then
  echo "Command failed (rc=$RC). See: ${OUT_FILE}"
  exit $RC
fi

echo "OK: ${STEP} (log: ${OUT_FILE})"
