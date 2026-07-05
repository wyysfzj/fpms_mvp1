# PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-FINAL-REGRESSION-20260705-01

Story Shape Classification
- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice
- Run final regression and close audit for P1.5 follow-up fee trigger implementation.
- Produce a design-item-to-task evidence ledger covering reexamination preview, grant/annuity deadline preview, and PCT/Hague/IC_LAYOUT non-enablement.

## Explicit Non-Closure
- No product code changes.
- No additional trigger implementation beyond the two completed P1.5 tasks.
- No PCT/Hague/IC_LAYOUT automatic trigger enablement.

## Remaining Follow-Up Task IDs
- PCT/Hague/IC_LAYOUT automatic trigger tasks remain future P2/P3 work pending customer samples and field confirmation.

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-FINAL-REGRESSION-20260705-01.md
- artifacts/PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-FINAL-REGRESSION-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-FINAL-REGRESSION-20260705-01.md`
- `cd backend && PYTHONPATH=. pytest tests/test_official_fee_preview_api.py tests/test_grant_fee_notice_task_creation.py tests/test_grant_fee_draft_linkage_api.py tests/test_annuity_generate.py -q`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-FINAL-REGRESSION-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-FOLLOWUP-TRIGGER-FINAL-REGRESSION-20260705-01/**

## Done Definition
- Targeted backend regression passes.
- Frontend typecheck and build pass.
- Evidence summary includes a close ledger and confirms PCT/Hague/IC_LAYOUT automatic triggers remain disabled/not implemented.
- Task gate passes.
