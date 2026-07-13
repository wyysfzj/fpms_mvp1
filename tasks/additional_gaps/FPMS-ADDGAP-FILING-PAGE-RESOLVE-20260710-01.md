# FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01

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

FilingPreparation 接收 case_id，调用 resolve API 获得 package_id，并以 replace 更新路由。

## Explicit Non-Closure

不增加 CaseDetail 入口，不改 filing 业务表单，不重做前端 API 模块。

## Dependencies

`FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01` 已 PASS。

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01`

## Allowed Files

- `frontend/src/api/officialWorkflows.ts`
- `frontend/src/api/officialWorkflows.types.ts`
- `frontend/src/modules/cases/pages/FilingPreparation.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-page-resolve.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 消费 OfficialWorkflow.Update。
- Status codes/errors: 消费 POST 200；对 404/409/422 使用简体中文错误反馈。
- Response envelope: 消费既有 filing package 输出。
- SQLite: N/A。
- Simplified Chinese UI: 所有新增/触及的可见文本必须为简体中文。

## Verification Commands

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-filing-page-resolve.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/officialWorkflows.ts frontend/src/api/officialWorkflows.types.ts frontend/src/modules/cases/pages/FilingPreparation.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-page-resolve.spec.ts`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
