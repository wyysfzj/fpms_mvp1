#!/usr/bin/env bash
set -euo pipefail
source scripts/_common.sh
source run_state.env
mkdir -p out

if [[ -n "${BILL_ID:-}" && "${BILL_ID}" != "null" ]]; then
  echo "== Print bill docx =="
  url="${BASE_URL}${API_PREFIX}/bills/${BILL_ID}/print"
  code=$(curl -sS -o "out/bill_${BILL_ID}.docx" -w "%{http_code}" -H "${AUTH_HEADER}" "${url}")
  if [[ "$code" == "409" ]]; then echo "WARN: bill template not configured (409)"; 
  elif [[ "$code" != "200" ]]; then echo "FAILED: bill print code=${code}"; exit 1; 
  else echo "OK: out/bill_${BILL_ID}.docx"; fi
fi

if [[ -n "${TASK_ID:-}" && "${TASK_ID}" != "null" ]]; then
  echo "== Print task sheet docx =="
  url="${BASE_URL}${API_PREFIX}/tasks/${TASK_ID}/print"
  code=$(curl -sS -o "out/task_${TASK_ID}.docx" -w "%{http_code}" -H "${AUTH_HEADER}" "${url}")
  if [[ "$code" == "409" ]]; then echo "WARN: task sheet template not configured (409)"; 
  elif [[ "$code" != "200" ]]; then echo "FAILED: task print code=${code}"; exit 1; 
  else echo "OK: out/task_${TASK_ID}.docx"; fi
fi
