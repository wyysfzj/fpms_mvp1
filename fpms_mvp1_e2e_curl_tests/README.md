# FPMS MVP1 — End-to-End curl Test Suite (PoC / SQLite)

This package provides an end-to-end, curl-based test suite with simulated data to validate MVP1 scope:
- Phase 3 Domain APIs
- Phase 3.1 apis_ext (admin/system/templates)
- Phase 3.5 business logic (docxtpl prints, document→task generation)

## Prerequisites
- Server running locally: http://localhost:8000
- API prefix assumed: /api/v1
- A valid token available in env: FPMS_TOKEN
- `curl` installed
- `jq` installed (recommended; scripts will fail fast if missing)

## Important notes
1) This suite does not assume a specific login endpoint. Set `FPMS_TOKEN` yourself.
2) Some payload field names may differ in your implementation (especially Documents/Fees/Billing). When a request fails with 422, update the corresponding JSON in `data/` to match your OpenAPI schema and re-run.
3) For Phase 3.5 prints, you must have real `.docx` template files on disk and configure their paths via system params.

## Quick start
```bash
export BASE_URL="http://localhost:8000"
export API_PREFIX="/api/v1"
export FPMS_TOKEN="<YOUR_TOKEN>"
cd fpms_mvp1_e2e_curl_tests

# Optional: set paths to templates for Phase 3.5 printing
export BILL_TEMPLATE_PATH="./backend/storage/templates/bill.docx"
export TASK_SHEET_TEMPLATE_PATH="./backend/storage/templates/task_sheet.docx"

bash scripts/00_prereq_check.sh
bash scripts/01_system_params_and_templates.sh
bash scripts/02_clients.sh
bash scripts/03_cases.sh
bash scripts/04_documents_and_autotasks.sh
bash scripts/05_tasks.sh
bash scripts/06_fees.sh
bash scripts/07_billing.sh
bash scripts/08_prints.sh
```

## Outputs
Scripts write created IDs to `run_state.env`. Source it to reuse IDs:
```bash
source run_state.env
echo "$CLIENT_ID $CASE_ID $DOC_ID $TASK_ID $BILL_ID"
```

