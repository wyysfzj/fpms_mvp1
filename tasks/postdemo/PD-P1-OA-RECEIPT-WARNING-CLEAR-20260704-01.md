# PD-P1-OA-RECEIPT-WARNING-CLEAR-20260704-01 — Hide stale OA receipt metadata warning after archive

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium

## chosen_runbook

`P0-frontend-heavy-story`

## Exact Closure Slice

When an OA reply work package has archive evidence satisfied, the receipt archive panel must not keep showing the stale form warning `缺少必填回执元数据`. The warning remains visible before receipt metadata is complete.

## Explicit Non-Closure

Do not change backend archive status rules, receipt persistence, CPC/OA direct submit, RPA, QR/signature automation, automatic official payment, Longxia email sending, or any unrelated P1 demo flow.

## Allowed Files

- `tasks/postdemo/PD-P1-OA-RECEIPT-WARNING-CLEAR-20260704-01.md`
- `frontend/src/modules/officialWorkflows/components/ReceiptArchivePanel.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.full-scope.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/pd-p1.live-backend.spec.ts`
- `artifacts/PD-P1-OA-RECEIPT-WARNING-CLEAR-20260704-01/**`

## Verification Commands

- Red: targeted Playwright P1 OA archive assertion fails before the UI condition is fixed.
- Green: targeted Playwright P1 full-scope contract test.
- Green: targeted Playwright P1 live-backend test if backend/frontend are available.
- TypeScript check for the Playwright harness.
- `./scripts/task_validate.sh PD-P1-OA-RECEIPT-WARNING-CLEAR-20260704-01`

## Done Definition

- The stale warning remains visible before receipt metadata is complete.
- After receipt metadata is recorded and archive evidence is satisfied, the warning is no longer visible.
- The fix is limited to the receipt archive panel and targeted E2E assertions.
- Required evidence exists under `artifacts/PD-P1-OA-RECEIPT-WARNING-CLEAR-20260704-01/**`.
- Task gate passes.

## Remaining Follow-Up Task IDs

None.
