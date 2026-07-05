# PD-FEE-SCENARIO-DEADLINE-RULES-20260705-01

Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice
- Enhance the existing official-fee preview response for `FILING_ACCEPTED` so each candidate carries the customer-confirmed structured rule metadata:
  - `fee_category`
  - `fee_subtype`
  - `trigger_rule`
  - `deadline_rule`
  - `reduction_scope`
- The application fee preview must expose the deadline rule as `申请日/受理通知起 2 个月`.
- The metadata must come from existing `FeeRate` fields where available, with service-layer defaults only for the confirmed `FILING_ACCEPTED` rule.

## Explicit Non-Closure
- No new database table.
- No new trigger events beyond existing `FILING_ACCEPTED`.
- No fee calculation behavior changes.
- No draft creation behavior changes.
- No PCT/Hague/IC automatic fee generation.
- No frontend UI rendering changes beyond API type contract metadata.

## Remaining Follow-Up Task IDs
- `PD-FEE-SCENARIO-REEXAM-TRIGGER-PREVIEW-20260705-01`
- `PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01`
- `PD-FEE-SCENARIO-PCT-HAGUE-TRIGGER-RULES-20260705-01`

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-DEADLINE-RULES-20260705-01.md
- backend/app/modules/fees/schemas.py
- backend/app/modules/fees/service.py
- backend/tests/test_official_fee_preview_api.py
- frontend/src/api/fees.types.ts
- artifacts/PD-FEE-SCENARIO-DEADLINE-RULES-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-DEADLINE-RULES-20260705-01.md`
- `cd backend && PYTHONPATH=. pytest tests/test_official_fee_preview_api.py -q`
- `cd frontend && npm run typecheck`
- `ruff check --fix backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/tests/test_official_fee_preview_api.py`
- `ruff format backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/tests/test_official_fee_preview_api.py`
- `ruff check backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/tests/test_official_fee_preview_api.py`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-DEADLINE-RULES-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-DEADLINE-RULES-20260705-01/**

## Done Definition
- Targeted API test proves `FILING_ACCEPTED` candidates include customer-facing category, subtype, trigger rule, deadline rule, and reduction scope.
- Targeted API test proves the application fee deadline is `申请日/受理通知起 2 个月`.
- Frontend typecheck proves the API contract extension is typed.
- Task gate and evidence artifacts pass.
