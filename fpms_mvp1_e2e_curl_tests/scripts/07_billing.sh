#!/usr/bin/env bash
set -euo pipefail
source scripts/_common.sh
source run_state.env
mkdir -p out

echo "== Billing: create manual bill (tries /bills/manual then /bills) =="
tmp="out/_bill_create_manual.json"
sed "s#\${CASE_ID}#${CASE_ID}#g; s#\${CLIENT_ID}#${CLIENT_ID}#g" data/bill_create_manual.json > "$tmp" || true

resp=$(api POST "/bills/manual" "$tmp" || true)
code=$(echo "$resp" | status_code || echo "")
if [[ "$code" == "" || "$code" == "404" ]]; then
  resp=$(api POST "/bills" "$tmp")
  code=$(echo "$resp" | status_code)
fi

if [[ "$code" != "200" && "$code" != "201" ]]; then echo "$resp"; exit 1; fi
bill_id=$(echo "$resp" | body | jq -r '.id // .bill_id // empty')
if [[ -n "$bill_id" && "$bill_id" != "null" ]]; then save_state_kv BILL_ID "$bill_id"; echo "OK: BILL_ID=$bill_id"; else echo "WARN: cannot extract BILL_ID; adjust jq"; fi

echo "== Billing: list bills =="
resp=$(api GET "/bills")
code=$(echo "$resp" | status_code)
assert_status 200 "$code"
