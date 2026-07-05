# PD-FEE-SCENARIO-FINAL-REGRESSION-20260705-01

Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice
- Run final regression and close audit for the updated official-fee scenario enhancement after the reduction semantics, structured FeeRate metadata, preview rule metadata, and completed catalog amount tasks.
- Produce an item-to-slice ledger mapping the approved updated design points to completed task evidence.

## Explicit Non-Closure
- No product code changes.
- No documentation rewrite beyond this task file and evidence summary.
- No new fee calculation, trigger event, UI, CPC/OA, RPA, signing, or payment behavior.

## Remaining Follow-Up Task IDs
- `PD-FEE-SCENARIO-REEXAM-TRIGGER-PREVIEW-20260705-01`
- `PD-FEE-SCENARIO-GRANT-ANNUITY-DEADLINE-PREVIEW-20260705-01`
- `PD-FEE-SCENARIO-PCT-HAGUE-TRIGGER-RULES-20260705-01`
- `PD-FEE-SCENARIO-IC-LAYOUT-TRIGGER-RULES-20260705-01`

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-FINAL-REGRESSION-20260705-01.md
- artifacts/PD-FEE-SCENARIO-FINAL-REGRESSION-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-FINAL-REGRESSION-20260705-01.md`
- `cd backend && PYTHONPATH=. pytest tests/test_apply_fee_draft_rule.py tests/test_apply_bill_readiness.py tests/test_apply_bill_unhappy.py tests/test_apply_fee_item_validation.py tests/test_apply_gov_paylist_readiness.py tests/test_b4_fee_rate_dims.py tests/test_official_fee_preview_api.py tests/test_official_fee_rate_catalog_seed.py tests/test_annuity_generate.py tests/test_grant_fee_draft_linkage_api.py tests/test_grant_fee_notice_task_creation.py -q`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-FINAL-REGRESSION-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-FINAL-REGRESSION-20260705-01/**

## Done Definition
- Backend fee scenario regression tests pass.
- Frontend typecheck and build pass.
- Evidence summary includes item-to-slice ledger and residual follow-ups.
- Task gate passes.
