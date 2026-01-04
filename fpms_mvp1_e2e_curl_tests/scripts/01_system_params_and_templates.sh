#!/usr/bin/env bash
set -euo pipefail
source scripts/_common.sh

echo "== System Params: default_locale =="
resp=$(api PUT "/system/params/default_locale" "data/system_param_default_locale.json")
code=$(echo "$resp" | status_code)
if [[ "$code" != "200" && "$code" != "201" ]]; then echo "$resp"; exit 1; fi
echo "OK: default_locale set"

mkdir -p out

if [[ -n "${BILL_TEMPLATE_PATH:-}" ]]; then
  tmp="out/_bill_template_path.json"
  sed "s#\${BILL_TEMPLATE_PATH}#${BILL_TEMPLATE_PATH}#g" data/system_param_bill_template_path.json > "$tmp" || true
  resp=$(api PUT "/system/params/bill_template_path" "$tmp")
  code=$(echo "$resp" | status_code)
  if [[ "$code" == "200" || "$code" == "201" ]]; then echo "OK: bill_template_path set"; else echo "WARN: bill_template_path failed (print may 409)"; fi
fi

if [[ -n "${TASK_SHEET_TEMPLATE_PATH:-}" ]]; then
  tmp="out/_task_sheet_template_path.json"
  sed "s#\${TASK_SHEET_TEMPLATE_PATH}#${TASK_SHEET_TEMPLATE_PATH}#g" data/system_param_task_sheet_template_path.json > "$tmp" || true
  resp=$(api PUT "/system/params/task_sheet_template_path" "$tmp")
  code=$(echo "$resp" | status_code)
  if [[ "$code" == "200" || "$code" == "201" ]]; then echo "OK: task_sheet_template_path set"; else echo "WARN: task_sheet_template_path failed (print may 409)"; fi
fi
