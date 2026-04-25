# W0-AUTO-PY-W0-TEMPLATE-P0-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Implement only the skeleton pytest handler for `TC-W0-010` in
`FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`.

The handler must create four run-scoped DocTemplate records through the real API
contract:

- `DS-TPL-DOC-001` / `OA_NOTICE`
- `DS-TPL-DOC-002` / `OA_REPLY`
- `DS-TPL-DOC-003` / `GRANT_NOTICE`
- `DS-TPL-DOC-005` / `ANNUITY_NOTICE`

The handler must use the existing `runtime.api`, `SeedCatalog`, `unique_code`,
and `runtime.db` read-only assertion capability. Generated `code` and `name`
values must include `runtime.run_id`, and `code` must not exceed the real
`t_doc_template.code` length of 64.

## Explicit Non-Closure Statement

This task does not implement any W0 handlers other than `TC-W0-010`, does not
change completed `TC-W0-001` or `TC-W0-007`, does not implement any `TC-A-*`
handler, does not modify YAML / JSON / schema assets, does not modify
Playwright, and does not modify real backend or frontend code. It does not add
framework API wrappers, DB helper capabilities, seed helper capabilities,
cleanup, or seed teardown.

## Remaining Follow-Up Task IDs

- `W0-AUTO-PY-W0-PERMISSION-P0-01`

## Allowed Files

- `tasks/automation/W0-AUTO-PY-W0-TEMPLATE-P0-01.md`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_w0.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_w0_doc_template_handler.py`
- `artifacts/W0-AUTO-PY-W0-TEMPLATE-P0-01/**`

## Verification Commands

```bash
cd FPMS_Automation_Skeleton_Pack
python3 scripts/validate_assets.py

cd FPMS_Automation_Skeleton_Pack/pytest_python
pytest tests/test_asset_integrity.py -q
pytest tests/test_auth_client_smoke.py -q
pytest tests/test_db_assert.py -q
pytest tests/test_helpers_runid_enum.py -q
pytest tests/test_seed_data.py -q
pytest tests/test_w0_client_handler.py -q
pytest tests/test_w0_fee_rate_handler.py -q
pytest tests/test_w0_doc_template_handler.py -q
pytest tests/test_wave_w0.py -k TC-W0-010 -q
```

Real backend smoke requires backend health first, a fresh `FPMS_RUN_ID`, and
`FPMS_DB_DSN=` unless a valid DSN is explicitly confirmed:

```bash
curl -sS http://127.0.0.1:8000/healthz
curl -sS http://127.0.0.1:8000/openapi.json

cd FPMS_Automation_Skeleton_Pack/pytest_python
FPMS_API_URL=http://127.0.0.1:8000/api/v1 \
FPMS_USERNAME=admin \
FPMS_PASSWORD=<set-locally> \
FPMS_RUN_ID=LOCAL-RUN-W0TPL-001 \
FPMS_DB_DSN= \
pytest tests/test_wave_w0.py -k TC-W0-010 -q
```

## Evidence Path

- `artifacts/W0-AUTO-PY-W0-TEMPLATE-P0-01/results.jsonl`
- `artifacts/W0-AUTO-PY-W0-TEMPLATE-P0-01/summary.md`
- `artifacts/W0-AUTO-PY-W0-TEMPLATE-P0-01/git/diff.patch`
- `artifacts/W0-AUTO-PY-W0-TEMPLATE-P0-01/baseline_allowlist.diff`
- `artifacts/W0-AUTO-PY-W0-TEMPLATE-P0-01/baseline_external_files.txt`
