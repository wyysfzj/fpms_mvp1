# PD-P1-E2E-DEMO-UI-VERIFY-20260612-01 — P1 demo UI E2E verification

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: medium
- `be_fe_coupling`: high
- `evidence_cost`: high

## chosen_runbook

`P0-frontend-heavy-story`

## Exact Closure Slice

Clear only explicitly named P1 demo/smoke fixture data, rebuild the `P1E2E-LIVE` demo dataset, execute the P1 demo UI end-to-end path against real Vue pages and live backend where available, and produce evidence that the UI matches `docs/postdemo/postdemo_p1_e2e_demo_20260612.md`.

## Explicit Non-Closure

Do not implement CPC/OA direct submit, RPA, QR/signature automation, automatic official payment, Longxia email sending, or P2/P3 integration. Do not delete non-demo production-like data. Do not absorb unrelated product fixes into this verification task; if an independent product bug is found, create a separate atomic task.

## Allowed Files

- `tasks/postdemo/PD-P1-E2E-DEMO-UI-VERIFY-20260612-01.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/package.json`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`
- `frontend/src/router/index.ts`
- `artifacts/PD-P1-E2E-DEMO-UI-VERIFY-20260612-01/**`

## Demo Data Safety Boundary

The seed/cleanup step may only delete records with these explicit fixture identifiers or direct children of those records:

- `P1E2E-LIVE`
- `CASE-PD-P1-LIVE`
- `CLIENT-PD-P1-LIVE`
- `CONTACT-PD-P1-LIVE`
- `APP-PD-P1-LIVE-1`
- `FILING-PD-P1-LIVE`
- `OA-PD-P1-LIVE`
- `FD-PD-P1-LIVE`
- `PL-PD-P1-LIVE`
- `DOC-FILING-PD-P1-LIVE`
- `DOC-OA-IN-PD-P1-LIVE`
- `DOC-OA-OUT-PD-P1-LIVE`
- `DOC-LETTER-PD-P1-LIVE`
- attachment/task/template/handoff IDs with the `PD-P1-LIVE` marker

`SMOKE-*` data is mentioned in the user request but must not be deleted unless the cleanup helper already has an explicit allowlisted identifier and the test proves it is a local smoke fixture.

## Verification Commands

- Seed cleanup/rebuild dry audit for explicit `PD-P1-LIVE` IDs.
- Targeted Playwright live-backend P1 demo UI test.
- TypeScript compile check for the Playwright test harness.
- `./scripts/task_validate.sh PD-P1-E2E-DEMO-UI-VERIFY-20260612-01`

## Done Definition

- Old P1 demo fixture data is cleared and the demo dataset is rebuilt in an idempotent way.
- The UI E2E path covers case edit, applicant masterdata, filing preparation, OA reply package, fee draft/pay-list, and letter handoff pages.
- Assertions verify key demo fields, Simplified Chinese UI text, P1 boundary messaging, and no forbidden P2/P3 automation claims.
- The discovered demo-entry route mismatch `/settings/applicants` is fixed only as a route alias to the existing applicant masterdata page; any other independent product bug is either fixed under a separate atomic task or recorded as a blocker/follow-up with evidence.
- Required evidence exists under `artifacts/PD-P1-E2E-DEMO-UI-VERIFY-20260612-01/**`.
- Task gate passes.

## Remaining Follow-Up Task IDs

None at task creation. Add explicit follow-up task IDs here if the E2E run discovers independent product bugs that cannot be fixed inside this verification slice.
