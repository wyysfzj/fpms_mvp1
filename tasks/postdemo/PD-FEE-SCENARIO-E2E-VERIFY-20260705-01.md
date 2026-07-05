# PD-FEE-SCENARIO-E2E-VERIFY-20260705-01

Story Shape Classification
- shared_file_density: medium
- prereq_dependency_density: medium
- be_fe_coupling: high
- evidence_cost: high
- chosen_runbook: P0-prereq-heavy-story

## Exact Closure Slice
- Extend the live-backend P1 Playwright verification so it proves the approved official-fee enhancement across backend fee data, application official-fee preview, existing fee draft/pay-list state, and the case fees UI node panel.

## Explicit Non-Closure
- No new product feature, database migration, CPC/OA direct submission, RPA, automatic signing, automatic payment, official payment Excel implementation, or P2/P3 fee-trigger expansion.
- No rewrite of the full P1 demo suite; only add the assertions and fixture data needed to verify the official-fee enhancement.

## Remaining Follow-Up Task IDs
- None for the approved P1.5 official-fee enhancement once this task passes.
- Future task ids must be created separately for P2/P3 fee-trigger expansion or official payment Excel upload.

## Allowed Files
- tasks/postdemo/PD-FEE-SCENARIO-E2E-VERIFY-20260705-01.md
- FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py
- FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts
- artifacts/PD-FEE-SCENARIO-E2E-VERIFY-20260705-01/**

## Verification Commands
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postdemo/PD-FEE-SCENARIO-E2E-VERIFY-20260705-01.md`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx tsc --noEmit`
- `cd backend && PYTHONPATH=. pytest tests/test_apply_fee_draft_rule.py tests/test_official_fee_preview_api.py tests/test_grant_fee_notice_task_creation.py tests/test_grant_fee_draft_linkage_api.py tests/test_annuity_generate.py tests/test_official_fee_rate_catalog_seed.py -q`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run demo:p1:seed`
- `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npm run test:pd-p1`
- `./scripts/task_validate.sh PD-FEE-SCENARIO-E2E-VERIFY-20260705-01`

## Evidence Path
- artifacts/PD-FEE-SCENARIO-E2E-VERIFY-20260705-01/**

## Done Definition
- Live seed creates official-fee-only demo data with FeeRate-backed candidate preview support.
- P1 live Playwright test verifies:
  - official fee preview API returns GOV-only candidates and an idempotency key;
  - case fees tab shows the official-fee node panel in Chinese;
  - existing application fee draft is GOV-only with no service fee;
  - pay-list boundary remains manual official payment / internal list;
  - grant and annuity backend targeted tests remain green.
- Task gate and evidence artifacts pass.
