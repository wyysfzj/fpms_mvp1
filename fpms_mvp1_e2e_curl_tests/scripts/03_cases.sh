#!/usr/bin/env bash
set -euo pipefail
source scripts/_common.sh
source run_state.env
mkdir -p out

echo "== Cases: create =="
tmp="out/_case_create.json"
sed "s#\${CLIENT_ID}#${CLIENT_ID}#g" data/case_create.json > "$tmp" || true
resp=$(api POST "/cases" "$tmp")
code=$(echo "$resp" | status_code)
if [[ "$code" != "200" && "$code" != "201" ]]; then echo "$resp"; exit 1; fi
case_id=$(echo "$resp" | body | jq -r '.id // .case_id // empty')
if [[ -z "$case_id" || "$case_id" == "null" ]]; then echo "$resp"; echo "FAILED: cannot extract CASE_ID"; exit 1; fi
save_state_kv CASE_ID "$case_id"
echo "OK: CASE_ID=$case_id"

echo "== Cases: list =="
resp=$(api GET "/cases")
code=$(echo "$resp" | status_code)
assert_status 200 "$code"

echo "== Cases: limited-edit (optional) =="
# Not strict: just demonstrate path existence if implemented
resp=$(api POST "/cases/${case_id}/limited-edit" "data/empty.json" || true)
echo "NOTE: limited-edit optional; response code: $(echo "$resp" | status_code || true)"
