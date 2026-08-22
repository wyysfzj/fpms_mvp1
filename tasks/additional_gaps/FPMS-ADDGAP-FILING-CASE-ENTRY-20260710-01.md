# FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 2
Executor role: Frontend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

CaseDetail 显示简体中文“申请前准备”动作，并携带当前 case_id 进入 filing 页面。

## Explicit Non-Closure

不改 FilingPreparation 内部逻辑，不新增权限模型，不增加其他案件动作。

## Dependencies

`FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01` 已 PASS。

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`

## Allowed Files

- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-case-entry.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用页面既有权限可见性；不得绕过后端 OfficialWorkflow.Update。
- Status codes/errors: N/A（导航）；目标页 API 状态由 Task 08 处理。
- Response envelope: N/A。
- SQLite: N/A。
- Simplified Chinese UI: 动作、错误和辅助文本必须为简体中文。

## Verification Commands

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-filing-case-entry.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/modules/cases/pages/CaseDetail.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-case-entry.spec.ts`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
