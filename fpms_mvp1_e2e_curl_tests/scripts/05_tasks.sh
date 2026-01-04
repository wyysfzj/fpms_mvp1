#!/usr/bin/env bash
set -euo pipefail
source scripts/_common.sh
source run_state.env
mkdir -p out

echo "== Tasks: create manual =="
tmp="out/_task_create.json"
sed "s#\${CASE_ID}#${CASE_ID}#g" data/task_create.json > "$tmp" || true
resp=$(api POST "/tasks" "$tmp")
code=$(echo "$resp" | status_code)
if [[ "$code" != "200" && "$code" != "201" ]]; then echo "$resp"; exit 1; fi
task_id=$(echo "$resp" | body | jq -r '.id // .task_id // empty')
if [[ -n "$task_id" && "$task_id" != "null" ]]; then save_state_kv TASK_ID "$task_id"; echo "OK: TASK_ID=$task_id"; else echo "WARN: cannot extract TASK_ID; adjust jq path"; fi

echo "== Tasks: today as worker =="
resp=$(api GET "/tasks/today?as=worker")
code=$(echo "$resp" | status_code)
assert_status 200 "$code"
echo "OK: tasks today worker"

echo "== Tasks: today invalid role (expect 400) =="
resp=$(api GET "/tasks/today?as=worker|supervisor")
code=$(echo "$resp" | status_code)
if [[ "$code" != "400" ]]; then echo "$resp"; echo "Expected 400"; exit 1; fi
echo "OK: invalid role rejected"
