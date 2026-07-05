# PD-FEE-SCENARIO-OFFICIAL-FEE-PREVIEW-20260705-01

Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice
- Add a backend official-fee preview API for the domestic filing/acceptance trigger (`FILING_ACCEPTED`) that returns official-fee-only candidate items, source event metadata, and an idempotency key without creating `FeeDraft` or `FeeItem` records.

## Explicit Non-Closure
- No frontend UI, fee node timeline, PayList/GovPayment generation, official payment Excel, CPC/OA direct submission, RPA, schema migration, or automatic persisted fee draft creation.
- No PCT, invalidation, restoration, extension, international design, compensation-period, or open-license preview trigger enablement in this task.

## Remaining Follow-Up Task IDs
- `PD-FEE-SCENARIO-FEE-NODE-UI-20260705-01`
- `PD-FEE-SCENARIO-E2E-VERIFY-20260705-01`
- Future trigger-expansion task if customer confirms P2/P3 official-fee events.

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-OFFICIAL-FEE-PREVIEW-20260705-01.md
- backend/app/modules/fees/api.py
- backend/app/modules/fees/schemas.py
- backend/app/modules/fees/service.py
- backend/tests/test_official_fee_preview_api.py
- artifacts/PD-FEE-SCENARIO-OFFICIAL-FEE-PREVIEW-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-OFFICIAL-FEE-PREVIEW-20260705-01.md`
- `pytest backend/tests/test_official_fee_preview_api.py -q`
- `python -m ruff check --fix backend/app/modules/fees/api.py backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/tests/test_official_fee_preview_api.py`
- `python -m ruff format backend/app/modules/fees/api.py backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/tests/test_official_fee_preview_api.py`
- `python -m ruff check backend/app/modules/fees/api.py backend/app/modules/fees/schemas.py backend/app/modules/fees/service.py backend/tests/test_official_fee_preview_api.py`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-OFFICIAL-FEE-PREVIEW-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-OFFICIAL-FEE-PREVIEW-20260705-01/**

## Done Definition
- A POST preview endpoint returns GOV-only candidate items for a supported domestic filing trigger.
- Response includes `trigger_event`, optional `source_document_id`, `idempotency_key`, `preview_only=true`, and total official fee amount.
- Running preview does not create any `FeeDraft` or `FeeItem` rows.
- Unsupported triggers return a business error instead of silently generating candidates.
