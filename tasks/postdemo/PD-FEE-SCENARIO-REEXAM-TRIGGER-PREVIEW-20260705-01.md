# PD-FEE-SCENARIO-REEXAM-TRIGGER-PREVIEW-20260705-01

Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice
- Extend official fee preview to support the domestic `REEXAM_REQUESTED` trigger.
- Select reexamination fee rate by patent type.
- Return Chinese trigger rule, deadline rule, fee category/subtype, fee reduction calculation fields, and source document information.
- Preserve preview-only behavior: no `FeeDraft` or `FeeItem` is created.

## Explicit Non-Closure
- No automatic reexamination work package creation.
- No reexamination request submission, CPC/OA direct submit, RPA, signing, or automatic payment.
- No PCT/Hague/IC_LAYOUT automatic trigger enablement.
- No database schema migration or fee draft persistence change.

## Remaining Follow-Up Task IDs
- `PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01`
- `PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-FINAL-REGRESSION-20260705-01`

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-REEXAM-TRIGGER-PREVIEW-20260705-01.md
- backend/app/modules/fees/schemas.py
- backend/app/modules/fees/service.py
- backend/tests/test_official_fee_preview_api.py
- frontend/src/api/fees.types.ts
- artifacts/PD-FEE-SCENARIO-REEXAM-TRIGGER-PREVIEW-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-REEXAM-TRIGGER-PREVIEW-20260705-01.md`
- `cd backend && PYTHONPATH=. pytest tests/test_official_fee_preview_api.py -q`
- `cd backend && python -m ruff check --fix app/modules/fees/schemas.py app/modules/fees/service.py tests/test_official_fee_preview_api.py`
- `cd backend && python -m ruff format app/modules/fees/schemas.py app/modules/fees/service.py tests/test_official_fee_preview_api.py`
- `cd backend && python -m ruff check app/modules/fees/schemas.py app/modules/fees/service.py tests/test_official_fee_preview_api.py`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-REEXAM-TRIGGER-PREVIEW-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-REEXAM-TRIGGER-PREVIEW-20260705-01/**

## Done Definition
- `REEXAM_REQUESTED` preview returns a single reexamination GOV candidate for INV/UM/DES domestic cases.
- `fee_reduction=0.85` is exposed as减缴 85% and payable 15%, with amount calculated accordingly.
- Response includes `source_document_id`, `trigger_rule=收到驳回决定且决定复审`, and `deadline_rule=驳回决定起 3 个月`.
- Unsupported triggers remain rejected.
- Preview does not create `FeeDraft` or `FeeItem`.
- Required evidence files and task gate exist.
