#!/usr/bin/env bash
set -euo pipefail
source scripts/_common.sh
source run_state.env
mkdir -p out

echo "== Documents: create OA (should auto-generate tasks) =="
tmp="out/_document_create_oa.json"
sed "s#\${CASE_ID}#${CASE_ID}#g" data/document_create_oa.json > "$tmp" || true
resp=$(api POST "/documents" "$tmp")
code=$(echo "$resp" | status_code)
if [[ "$code" != "200" && "$code" != "201" ]]; then echo "$resp"; exit 1; fi
doc_id=$(echo "$resp" | body | jq -r '.id // .document_id // empty')
if [[ -n "$doc_id" && "$doc_id" != "null" ]]; then save_state_kv DOC_ID "$doc_id"; echo "OK: DOC_ID=$doc_id"; else echo "WARN: cannot extract DOC_ID; adjust jq path"; fi

echo "== Tasks: list (auto-created tasks may appear) =="
resp=$(api GET "/tasks")
code=$(echo "$resp" | status_code)
assert_status 200 "$code"
