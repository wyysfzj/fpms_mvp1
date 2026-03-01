#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000/api/v1}"
USERNAME="${FPMS_USERNAME:-admin}"
PASSWORD="${FPMS_PASSWORD:-admin123}"
BILL_ID="${1:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TEMPLATE_PATH="${REPO_ROOT}/backend/storage/templates/bill_default.docx"
TEMPLATE_NAME="Bill Print Default"
TEMPLATE_GROUP="BILL"
TEMPLATE_LANG="en"

log() {
  printf '[setup_printing] %s\n' "$*"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "missing required command: $1"
    exit 1
  fi
}

require_cmd curl
require_cmd jq
require_cmd python3

log "ensuring bill template file exists at ${TEMPLATE_PATH}"
python3 - "${TEMPLATE_PATH}" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)

if path.exists():
    print(f"Template already exists: {path}")
    raise SystemExit(0)

try:
    from docx import Document
except Exception as exc:  # pragma: no cover
    print(f"python-docx import failed: {exc}", file=sys.stderr)
    raise SystemExit(1)

doc = Document()
doc.add_heading("FPMS Bill", level=1)
doc.add_paragraph("Bill No: {{ bill_no }}")
doc.add_paragraph("Client: {{ client_name }}")
doc.add_paragraph("Currency: {{ currency }}")
doc.add_paragraph("Issue Date: {{ issue_date }}")
doc.add_paragraph("Total: {{ total_amount }}")
doc.save(path)
print(f"Created template: {path}")
PY

log "logging in at ${BASE_URL}/auth/login"
LOGIN_CODE="$(curl -sS -o /tmp/setup_printing_login.json -w '%{http_code}' \
  -X POST "${BASE_URL}/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}")"
if [[ "${LOGIN_CODE}" != "200" ]]; then
  log "login failed with status ${LOGIN_CODE}"
  cat /tmp/setup_printing_login.json
  exit 1
fi
TOKEN="$(jq -r '.access_token // empty' /tmp/setup_printing_login.json)"
if [[ -z "${TOKEN}" ]]; then
  log "access_token not found in login response"
  cat /tmp/setup_printing_login.json
  exit 1
fi
log "login ok (token prefix: ${TOKEN:0:12}..., len=${#TOKEN})"

AUTH_HEADER="Authorization: Bearer ${TOKEN}"

if [[ -z "${BILL_ID}" ]]; then
  log "resolving bill id from ${BASE_URL}/bills?page=1&page_size=1"
  BILLS_CODE="$(curl -sS -o /tmp/setup_printing_bills.json -w '%{http_code}' \
    -H "${AUTH_HEADER}" \
    "${BASE_URL}/bills?page=1&page_size=1")"
  if [[ "${BILLS_CODE}" != "200" ]]; then
    log "bill list failed with status ${BILLS_CODE}"
    cat /tmp/setup_printing_bills.json
    exit 1
  fi
  BILL_ID="$(jq -r '.items[0].id // empty' /tmp/setup_printing_bills.json)"
  if [[ -z "${BILL_ID}" ]]; then
    log "no bills found; provide BILL_ID as first argument after creating a bill"
    exit 1
  fi
fi
log "using bill id: ${BILL_ID}"

log "ensuring at least one letterhead exists"
LETTERHEADS_CODE="$(curl -sS -o /tmp/setup_printing_letterheads.json -w '%{http_code}' \
  -H "${AUTH_HEADER}" \
  "${BASE_URL}/letterheads")"
if [[ "${LETTERHEADS_CODE}" != "200" ]]; then
  log "list letterheads failed with status ${LETTERHEADS_CODE}"
  cat /tmp/setup_printing_letterheads.json
  exit 1
fi
LETTERHEAD_COUNT="$(jq 'length' /tmp/setup_printing_letterheads.json)"
if [[ "${LETTERHEAD_COUNT}" == "0" ]]; then
  log "creating default letterhead"
  CREATE_LETTERHEAD_CODE="$(curl -sS -o /tmp/setup_printing_letterhead_create.json -w '%{http_code}' \
    -X POST "${BASE_URL}/letterheads" \
    -H "${AUTH_HEADER}" \
    -H 'Content-Type: application/json' \
    -d '{"name":"Default Letterhead","locale":"en","header_text":"FPMS","is_default":true}')"
  if [[ "${CREATE_LETTERHEAD_CODE}" != "201" ]]; then
    log "create letterhead failed with status ${CREATE_LETTERHEAD_CODE}"
    cat /tmp/setup_printing_letterhead_create.json
    exit 1
  fi
else
  log "letterhead already present (count=${LETTERHEAD_COUNT})"
fi

log "ensuring template record points to bill template file"
TEMPLATES_CODE="$(curl -sS -o /tmp/setup_printing_templates.json -w '%{http_code}' \
  -H "${AUTH_HEADER}" \
  "${BASE_URL}/templates?page=1&page_size=100")"
if [[ "${TEMPLATES_CODE}" != "200" ]]; then
  log "list templates failed with status ${TEMPLATES_CODE}"
  cat /tmp/setup_printing_templates.json
  exit 1
fi
TEMPLATE_MATCH_COUNT="$(jq \
  --arg p "${TEMPLATE_PATH}" \
  --arg name "${TEMPLATE_NAME}" \
  --arg group "${TEMPLATE_GROUP}" \
  '[.items[]? | select((.file_path? // "") == $p or ((.name // "") == $name and (.group // "") == $group))] | length' \
  /tmp/setup_printing_templates.json)"
if [[ "${TEMPLATE_MATCH_COUNT}" == "0" ]]; then
  log "creating template record for ${TEMPLATE_PATH}"
  CREATE_TEMPLATE_CODE="$(curl -sS -o /tmp/setup_printing_template_create.json -w '%{http_code}' \
    -X POST "${BASE_URL}/templates" \
    -H "${AUTH_HEADER}" \
    -H 'Content-Type: application/json' \
    -d "$(jq -nc \
      --arg name "${TEMPLATE_NAME}" \
      --arg group "${TEMPLATE_GROUP}" \
      --arg lang "${TEMPLATE_LANG}" \
      --arg fp "${TEMPLATE_PATH}" \
      '{name:$name, group:$group, language:$lang, file_path:$fp, enabled:true}')")"
  if [[ "${CREATE_TEMPLATE_CODE}" != "201" ]]; then
    log "create template failed with status ${CREATE_TEMPLATE_CODE}"
    cat /tmp/setup_printing_template_create.json
    exit 1
  fi
else
  log "template record already present (count=${TEMPLATE_MATCH_COUNT})"
fi

log "upserting system param bill_template_path"
UPSERT_PARAM_CODE="$(curl -sS -o /tmp/setup_printing_param_upsert.json -w '%{http_code}' \
  -X PUT "${BASE_URL}/system/params/bill_template_path" \
  -H "${AUTH_HEADER}" \
  -H 'Content-Type: application/json' \
  -d "$(jq -nc --arg fp "${TEMPLATE_PATH}" \
    '{param_value:$fp, value_type:"string", description:"Bill print template path", is_secret:false}')")"
if [[ "${UPSERT_PARAM_CODE}" != "200" ]]; then
  log "upsert system param failed with status ${UPSERT_PARAM_CODE}"
  cat /tmp/setup_printing_param_upsert.json
  exit 1
fi

log "verifying bill print success"
PRINT_CODE="$(curl -sS -D /tmp/setup_printing_print_headers.txt -o /tmp/setup_printing_print_body.bin -w '%{http_code}' \
  -H "${AUTH_HEADER}" \
  "${BASE_URL}/bills/${BILL_ID}/print")"
PRINT_REQUEST_ID="$(awk -F': ' 'tolower($1) == "x-request-id" {gsub("\r","",$2); print $2}' /tmp/setup_printing_print_headers.txt | tail -n 1)"
if [[ "${PRINT_CODE}" != "200" ]]; then
  log "print failed with status ${PRINT_CODE}; x-request-id=${PRINT_REQUEST_ID:-n/a}"
  if file /tmp/setup_printing_print_body.bin | grep -Eqi 'json|text'; then
    cat /tmp/setup_printing_print_body.bin
  else
    log "print response is binary; saved at /tmp/setup_printing_print_body.bin"
  fi
  exit 1
fi

PRINT_SIZE="$(wc -c < /tmp/setup_printing_print_body.bin | tr -d ' ')"
log "print OK: status=200, x-request-id=${PRINT_REQUEST_ID:-n/a}, bytes=${PRINT_SIZE}"
log "setup complete"
