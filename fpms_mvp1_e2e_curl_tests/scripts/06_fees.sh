#!/usr/bin/env bash
set -euo pipefail
source scripts/_common.sh
source run_state.env
mkdir -p out

echo "== Fees: create draft =="
tmp="out/_fee_draft_create.json"
sed "s#\${CASE_ID}#${CASE_ID}#g; s#\${CLIENT_ID}#${CLIENT_ID}#g" data/fee_draft_create.json > "$tmp" || true
resp=$(api POST "/fees/drafts" "$tmp")
code=$(echo "$resp" | status_code)
if [[ "$code" != "200" && "$code" != "201" ]]; then echo "$resp"; exit 1; fi
draft_id=$(echo "$resp" | body | jq -r '.id // .draft_id // empty')
if [[ -n "$draft_id" && "$draft_id" != "null" ]]; then save_state_kv FEE_DRAFT_ID "$draft_id"; echo "OK: FEE_DRAFT_ID=$draft_id"; else echo "WARN: cannot extract FEE_DRAFT_ID; adjust jq"; fi

if [[ -n "${draft_id:-}" && "${draft_id}" != "null" ]]; then
  echo "== Fees: add item to draft =="
  resp=$(api POST "/fees/drafts/${draft_id}/items" "data/fee_draft_add_item.json")
  code=$(echo "$resp" | status_code)
  if [[ "$code" != "200" && "$code" != "201" ]]; then echo "$resp"; exit 1; fi
  item_id=$(echo "$resp" | body | jq -r '.id // .item_id // empty')
  if [[ -n "$item_id" && "$item_id" != "null" ]]; then save_state_kv FEE_ITEM_ID "$item_id"; echo "OK: FEE_ITEM_ID=$item_id"; fi
fi

echo "== Fees: list drafts =="
resp=$(api GET "/fees/drafts")
code=$(echo "$resp" | status_code)
assert_status 200 "$code"
