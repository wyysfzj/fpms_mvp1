# FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 7
Executor role: Frontend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

GrantFeeTaskList 以简体中文展示 source/deadline/legacy/superseded lineage。

## Explicit Non-Closure

不提供 replacement action，不改变 workflow status 显示语义，不修改 backend。

## Dependencies

- 41
- 42

## Remaining Follow-Up Task IDs

- 44

## Allowed Files

- `frontend/src/api/grantFees.ts`
- `frontend/src/api/grantFees.types.ts`
- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-lineage-ui.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime Contracts

- Permission: 消费 GrantFeeTask.Read。
- Status codes/errors: 消费 GET 200；错误提示简体中文。
- Response envelope: 消费扩展后的 list/state 模型。
- SQLite: N/A。
- Simplified Chinese UI: 所有 lineage 标签、空态和提示必须为简体中文。

## Verification Commands

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-lineage-ui.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/grantFees.ts frontend/src/api/grantFees.types.ts frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-lineage-ui.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01/**`

## Done Definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
