# FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before Task 46
Executor role: Frontend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-frontend-heavy-story`

## Exact Closure Slice

Make the existing GrantFeeTaskList ordinary mutation controls fail closed for non-confirmed lineage:
legacy/superseded rows cannot be selected for batch client instruction/notice generation and cannot
invoke direct draft generation or mark-done; the page displays a Simplified Chinese reason. Confirmed
rows preserve all existing ordinary actions.

## Explicit Non-Closure

Do not change backend/API/types, workflow status, replacement action/dialog, permission rules,
lineage display labels, filters, or any other page/test. Do not remove rows from the list.

## Dependencies

- `FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01` (`PASS` required before shared-file edit)
- `FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01` (`PASS` required before acceptance)

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/**`

No other source, test, task, plan, manifest, or artifact family is authorized.

## Runtime Contracts

- `lineage_status === CONFIRMED` is required for existing direct and batch mutation controls.
- Legacy/superseded rows remain visible; their ordinary mutation controls are disabled or omitted and
  the row exposes “来源未确认或已被替代，不能执行授权费操作”.
- Batch selection itself rejects non-confirmed rows, so mixed selections cannot reach an API call.
- Existing permission checks, replacement action rules, workflow status, and confirmed-row behavior remain unchanged.
- All new user-visible text is Simplified Chinese.

## Verification Commands

- RED/GREEN: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts --workers=1`
- Regression: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-lineage-ui.spec.ts src/tests/addgap-grant-replacement-ui.spec.ts src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-mutation-lineage-ui-gate.spec.ts tasks/additional_gaps/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/**`

## Supplemental Close Contract

This task is outside the frozen 47-entry manifest. It must independently pass review, evidence
validation, and its task gate before Task46 starts; Task47 must record it in the supplemental appendix.

## Done Definition

RED proves all direct/batch UI bypasses; GREEN proves legacy/superseded controls cannot call APIs,
confirmed controls remain functional, replacement/lineage regressions stay green, and scoped
checks/review/evidence/gate pass. Only then may this task be `PASS`.
