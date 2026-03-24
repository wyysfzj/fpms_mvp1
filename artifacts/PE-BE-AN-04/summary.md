# PE-BE-AN-04 Evidence Summary

## Task
- ID: PE-BE-AN-04
- Runbook: `tasks/postenhancement/backend/PE-BE-AN-04.md`

## Scope Compliance
- Product-code changes restricted to allowlist:
  - `backend/app/modules/annuity/service.py`

## Implemented
- Added annuity draft-generation service:
  - `generate_fee_drafts_from_annuity_tasks(...)`
- Supports `pay_next_year` option:
  - For each selected task, optionally resolves and processes the same-case next-year annuity task.
- Idempotence control:
  - Uses deterministic task/year markers (`ANNUITY_TASK:{task_id};YEAR:{year_no}`) on generated fee items.
  - Skips duplicate generation via existing marker detection and in-request duplicate target control.
- Batch result contract for upcoming endpoint:
  - Returns `summary` and per-task `success` / `failed` detail arrays.
- Compatibility:
  - Existing annuity listing/instruction behavior remains unchanged.

## Verification
- `cd backend && python3 -m py_compile app/modules/annuity/service.py` -> PASS
- `cd backend && pytest -q` -> PASS (`141 passed, 3 warnings in 30.20s`)
