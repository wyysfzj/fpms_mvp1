# PD-P1-E2E-DEMO-RISK-CLOSE-20260612-01 — P1 demo residual risk close

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: medium
- `be_fe_coupling`: test/docs only
- `evidence_cost`: high

## chosen_runbook

`P0-frontend-heavy-story`

## Exact Closure Slice

Close the actionable residual risks found during the prior P1 demo UI E2E run: fix the Playwright full-scope typecheck error, add a safe demo seed command, document mandatory pre-demo seed/cleanup and smoke cleanup boundaries, add the missing applicant masterdata search UI that is already supported by the API, update the live E2E and demo script to locate the demo applicant through search instead of relying on first-page sort order, and create a dedicated follow-up task for safe `SMOKE-*` cleanup allowlisting.

## Explicit Non-Closure

No backend product feature implementation beyond test harness and documentation alignment. Frontend product change is limited to the applicant masterdata list search input backed by the existing `q` API parameter. No CPC/OA direct submit, RPA, QR/signature automation, automatic official payment, Longxia email sending, P2/P3 integration, or wildcard data cleanup. Do not delete real data or unproven `SMOKE-*` records.

## Allowed Files

- `tasks/postdemo/PD-P1-E2E-DEMO-RISK-CLOSE-20260612-01.md`
- `tasks/postdemo/PD-P1-E2E-SAFE-SMOKE-CLEANUP-20260612-01.md`
- `docs/postdemo/postdemo_p1_e2e_demo_20260612.md`
- `docs/postdemo/postdemo_p1_e2e_demo_20260612.docx`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/package.json`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.full-scope.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `frontend/src/modules/settings/pages/ApplicantList.vue`
- `artifacts/PD-P1-E2E-DEMO-RISK-CLOSE-20260612-01/**`

## Verification Commands

- Red: full Playwright harness `npx tsc --noEmit` before type fix.
- Green: full Playwright harness `npx tsc --noEmit` after type fix.
- Targeted live E2E compile and/or run for applicant search flow.
- Demo seed npm script smoke check.
- Demo document structural check, including DOCX text check.
- `./scripts/task_validate.sh PD-P1-E2E-DEMO-RISK-CLOSE-20260612-01`

## Done Definition

- `pd-p1.full-scope.spec.ts` no longer blocks full Playwright TypeScript checking.
- Demo seed command is available from the Playwright package and documented.
- Demo documentation states that pre-demo seed/cleanup is mandatory and restricted to fixed `PD-P1-LIVE` IDs.
- Demo documentation says `SMOKE-*` cleanup requires explicit allowlist and no wildcard deletion.
- Applicant masterdata page has a Simplified Chinese search input, and demo/live E2E use search to locate `P1测试申请人有限公司`, so visibility does not depend on first-page sort order.
- Dedicated safe smoke cleanup follow-up task exists with explicit closure/non-closure and allowlist design.
- Required evidence artifacts exist and task gate passes.

## Remaining Follow-Up Task IDs

- `PD-P1-E2E-SAFE-SMOKE-CLEANUP-20260612-01`
