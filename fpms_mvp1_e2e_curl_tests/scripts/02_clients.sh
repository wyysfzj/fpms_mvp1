#!/usr/bin/env bash
set -euo pipefail
source scripts/_common.sh
rm -f run_state.env
mkdir -p out

echo "== Clients: create =="
resp=$(api POST "/clients" "data/client_create.json")
code=$(echo "$resp" | status_code)
if [[ "$code" != "200" && "$code" != "201" ]]; then echo "$resp"; exit 1; fi
cid=$(echo "$resp" | body | jq -r '.id // .client_id // empty')
if [[ -z "$cid" || "$cid" == "null" ]]; then echo "$resp"; echo "FAILED: cannot extract CLIENT_ID"; exit 1; fi
save_state_kv CLIENT_ID "$cid"
echo "OK: CLIENT_ID=$cid"

echo "== Clients: list =="
resp=$(api GET "/clients")
code=$(echo "$resp" | status_code)
assert_status 200 "$code"

echo "== Clients: update =="
resp=$(api PUT "/clients/${cid}" "data/client_update.json")
code=$(echo "$resp" | status_code)
if [[ "$code" != "200" ]]; then echo "$resp"; exit 1; fi
echo "OK: client updated"
